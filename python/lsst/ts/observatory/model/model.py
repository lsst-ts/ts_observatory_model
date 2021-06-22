# This file is part of ts_observatory_model.
#
# Developed for the Vera Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License

import logging
import math
import numpy as np
import os

import palpy as pal

from lsst.ts.dateloc import DateProfile, ObservatoryLocation
from lsst.ts.observatory.model import ObservatoryModelParameters
from lsst.ts.observatory.model import ObservatoryPosition
from lsst.ts.observatory.model import ObservatoryState
from lsst.ts.observatory.model import read_conf_file

__all__ = ["ObservatoryModel"]

TWOPI = 2 * np.pi

class ObservatoryModel(object):
    """Class for modeling the observatory.
    """

    def __init__(self, location=None, log_level=logging.DEBUG):
        """Initialize the class.

        Parameters
        ----------
        location : lsst.ts.dateloc.ObservatoryLocation, optional
            An instance of the observatory location. Default is None,
            but this sets up the LSST as the location.
        log_level : int
            Set the logging level for the class. Default is logging.DEBUG.
        """
        self.log = logging.getLogger("ObservatoryModel")
        self.log_level = log_level

        self.params = ObservatoryModelParameters()
        if location is None:
            self.location = ObservatoryLocation()
            self.location.for_lsst()
        else:
            self.location = location
        self.park_state = ObservatoryState()
        self.current_state = ObservatoryState()

        self.dateprofile = DateProfile(0.0, self.location)

        self.filters = ["u", "g", "r", "i", "z", "y"]

        self.activities = ["telalt",
                           "telaz",
                           "telrot",
                           "telsettle",
                           "telopticsopenloop",
                           "telopticsclosedloop",
                           "domalt",
                           "domaz",
                           "domazsettle",
                           "filter",
                           "readout",
                           "exposures"]
        self.function_get_delay_for = {}
        self.delay_for = {}
        self.longest_prereq_for = {}
        for activity in self.activities:
            function_name = "get_delay_for_" + activity
            self.function_get_delay_for[activity] = getattr(self, function_name)
            self.delay_for[activity] = 0.0
            self.longest_prereq_for[activity] = ""
        self.lastslew_delays_dict = {}
        self.lastslew_criticalpath = []
        self.filter_changes_list = []

    def __str__(self):
        """str: The string representation of the model."""
        return str(self.current_state)

    @classmethod
    def get_configure_dict(cls):
        """Get the configuration dictionary for the observatory model.

        Returns
        -------
        dict
            The configuration dictionary for the observatory model.
        """
        conf_file = os.path.join(os.path.dirname(__file__),
                                 "observatory_model.conf")
        conf_dict = read_conf_file(conf_file)
        return conf_dict

    def altaz2radecpa(self, dateprofile, alt_rad, az_rad):
        """Converts alt, az coordinates into ra, dec for the given time.

        Parameters
        ----------
        dateprofile : lsst.ts.dateloc.DateProfile
            Instance containing the time information.
        alt_rad : float
            The altitude in radians
        az_rad : float
            The azimuth in radians

        Returns
        -------
        tuple(float, float, float)
            (right ascension in radians, declination in radians, parallactic angle in radians)
        """
        lst_rad = dateprofile.lst_rad

        (ha_rad, dec_rad) = pal.dh2e(az_rad, alt_rad, self.location.latitude_rad)
        pa_rad = divmod(pal.pa(ha_rad, dec_rad, self.location.latitude_rad), TWOPI)[1]
        ra_rad = divmod(lst_rad - ha_rad, TWOPI)[1]

        return (ra_rad, dec_rad, pa_rad)

    @staticmethod
    def compute_kinematic_delay(distance, maxspeed, accel, decel, free_range=0.):
        """Calculate the kinematic delay.

        This function calculates the kinematic delay for the given distance
        based on a simple second-order function for velocity plus an additional
        optional free range. The model considers that the free range is used for crawling
        such that:

            1 - If the distance is less than the free_range, than the delay is zero.
            2 - If the distance is larger than the free_range, than the initial and final speed
                are equal to that possible to achieve after accelerating/decelerating for the free_range
                distance.


        Parameters
        ----------
        distance : float
            The required distance to move.
        maxspeed : float
            The maximum speed for the calculation.
        accel : float
            The acceleration for the calculation.
        decel : float
            The deceleration for the calculation.
        free_range : float
            The free range in which the kinematic model returns zero delay.

        Returns
        -------
        tuple(float, float)
            (delay time in seconds, peak velocity in radians/sec)
        """
        d = abs(distance)
        vpeak_free_range = (2 * free_range / (1 / accel + 1 / decel)) ** 0.5
        if vpeak_free_range > maxspeed:
            vpeak_free_range = maxspeed

        if free_range > d:
            return 0., vpeak_free_range

        vpeak = (2 * d / (1 / accel + 1 / decel)) ** 0.5

        if vpeak <= maxspeed:
            delay = (vpeak - vpeak_free_range) * (1. / accel + 1. / decel)
        else:
            d1 = 0.5 * (maxspeed * maxspeed) / accel - free_range * accel / (accel + decel)
            d3 = 0.5 * (maxspeed * maxspeed) / decel - free_range * decel / (accel + decel)

            if d1 < 0.:
                # This means it is possible to ramp up to max speed in less than the free range
                d1 = 0.
            if d3 < 0.:
                # This means it is possible to break down to zero in less than the free range
                d3 = 0.

            d2 = d - d1 - d3 - free_range

            t1 = (maxspeed - vpeak_free_range) / accel
            t3 = (maxspeed - vpeak_free_range) / decel
            t2 = d2 / maxspeed

            delay = t1 + t2 + t3
            vpeak = maxspeed

        if distance < 0.:
            vpeak *= -1.

        return delay, vpeak

    def _uamSlewTime(self, distance, vmax, accel):
        """Compute slew time delay assuming uniform acceleration (for any component).
        If you accelerate uniformly to vmax, then slow down uniformly to zero, distance traveled is
        d  = vmax**2 / accel
        To travel distance d while accelerating/decelerating at rate a, time required is t = 2 * sqrt(d / a)
        If hit vmax, then time to acceleration to/from vmax is 2*vmax/a and distance in those
        steps is vmax**2/a. The remaining distance is (d - vmax^2/a) and time needed is (d - vmax^2/a)/vmax

        This method accepts arrays of distance, and assumes acceleration == deceleration.

        Parameters
        ----------
        distance : numpy.ndarray
            Distances to travel. Must be positive value.
        vmax : float
            Max velocity
        accel : float
            Acceleration (and deceleration)

        Returns
        -------
        numpy.ndarray
        """
        dm = vmax**2 / accel
        slewTime = np.where(distance < dm, 2 * np.sqrt(distance / accel),
                            2 * vmax / accel + (distance - dm) / vmax)
        return slewTime

    def get_approximate_slew_delay(self, alt_rad, az_rad, goal_filter, lax_dome=False):
        """Calculates ``slew'' time to a series of alt/az/filter positions.
        Assumptions (currently):
            assumes rotator is not moved (no rotator included)
            assumes  we never max out cable wrap-around!

        Calculates the ``slew'' time necessary to get from current state
        to alt2/az2/filter2. The time returned is actually the time between
        the end of an exposure at current location and the beginning of an exposure
        at alt2/az2, since it includes readout time in the ``slew'' time.

        Parameters
        ----------
        alt_rad : np.ndarray
            The altitude of the destination pointing in RADIANS.
        az_rad : np.ndarray
            The azimuth of the destination pointing in RADIANS.
        goal_filter : np.ndarray
            The filter to be used in the destination observation.
        lax_dome : boolean, default False
            If True, allow the dome to creep, model a dome slit, and don't
            require the dome to settle in azimuth. If False, adhere to the way
            SOCS calculates slew times (as of June 21 2017).

        Returns
        -------
        np.ndarray
            The number of seconds between the two specified exposures.
        """
        # FYI this takes on the order of 285 us to calculate slew times to 2293 pts (.12us per pointing)
        # Find the distances to all the other fields.
        deltaAlt = np.abs(alt_rad - self.current_state.alt_rad)
        deltaAz = np.abs(az_rad - self.current_state.az_rad)
        deltaAz = np.minimum(deltaAz, np.abs(deltaAz - 2 * np.pi))

        # Calculate how long the telescope will take to slew to this position.
        telAltSlewTime = self._uamSlewTime(deltaAlt, self.params.telalt_maxspeed_rad,
                                           self.params.telalt_accel_rad )
        telAzSlewTime = self._uamSlewTime(deltaAz, self.params.telaz_maxspeed_rad,
                                          self.params.telaz_accel_rad)
        totTelTime = np.maximum(telAltSlewTime, telAzSlewTime)
        # Time for open loop optics correction
        olTime = deltaAlt / self.params.optics_ol_slope
        totTelTime += olTime
        # Add time for telescope settle.
        settleAndOL = np.where(totTelTime > 0)
        totTelTime[settleAndOL] += np.maximum(0, self.params.mount_settletime - olTime[settleAndOL])
        # And readout puts a floor on tel time
        totTelTime = np.maximum(self.params.readouttime, totTelTime)

        # now compute dome slew time
        if lax_dome:
            totDomeTime = np.zeros(len(alt_rad), float)
            # model dome creep, dome slit, and no azimuth settle
            # if we can fit both exposures in the dome slit, do so
            sameDome = np.where(deltaAlt ** 2 + deltaAz ** 2 < self.params.camera_fov ** 2)

            # else, we take the minimum time from two options:
            # 1. assume we line up alt in the center of the dome slit so we
            #    minimize distance we have to travel in azimuth.
            # 2. line up az in the center of the slit
            # also assume:
            # * that we start out going maxspeed for both alt and az
            # * that we only just barely have to get the new field in the
            #   dome slit in one direction, but that we have to center the
            #   field in the other (which depends which of the two options used)
            # * that we don't have to slow down until after the shutter
            #   starts opening
            domDeltaAlt = deltaAlt
            # on each side, we can start out with the dome shifted away from
            # the center of the field by an amount domSlitRadius - fovRadius
            domSlitDiam = self.params.camera_fov / 2.0
            domDeltaAz = deltaAz - 2 * (domSlitDiam / 2 - self.params.camera_fov / 2)
            domAltSlewTime = domDeltaAlt / self.params.domalt_maxspeed_rad
            domAzSlewTime = domDeltaAz / self.params.domaz_maxspeed_rad
            totDomTime1 = np.maximum(domAltSlewTime, domAzSlewTime)

            domDeltaAlt = deltaAlt - 2 * (domSlitDiam / 2 - self.params.camera_fov / 2)
            domDeltaAz = deltaAz
            domAltSlewTime = domDeltaAlt / self.params.domalt_maxspeed_rad
            domAzSlewTime = domDeltaAz / self.params.domaz_maxspeed_rad
            totDomTime2 = np.maximum(domAltSlewTime, domAzSlewTime)

            totDomTime = np.minimum(totDomTime1, totDomTime2)
            totDomTime[sameDome] = 0

        else:
            # the above models a dome slit and dome creep. However, it appears that
            # SOCS requires the dome to slew exactly to each field and settle in az
            domAltSlewTime = self._uamSlewTime(deltaAlt, self.params.domalt_maxspeed_rad,
                                               self.params.domalt_accel_rad)
            domAzSlewTime = self._uamSlewTime(deltaAz, self.params.domaz_maxspeed_rad,
                                              self.params.domaz_accel_rad)
            # Dome takes 1 second to settle in az
            domAzSlewTime = np.where(domAzSlewTime > 0,
                                     domAzSlewTime + self.params.domaz_settletime,
                                     domAzSlewTime)
            totDomTime = np.maximum(domAltSlewTime, domAzSlewTime)
        # Find the max of the above for slew time.
        slewTime = np.maximum(totTelTime, totDomTime)
        # include filter change time if necessary
        filterChange = np.where(goal_filter != self.current_state.filter)
        slewTime[filterChange] = np.maximum(slewTime[filterChange],
                                            self.params.filter_changetime)
        # Add closed loop optics correction
        # Find the limit where we must add the delay
        cl_limit = self.params.optics_cl_altlimit[1]
        cl_delay = self.params.optics_cl_delay[1]
        closeLoop = np.where(deltaAlt >= cl_limit)
        slewTime[closeLoop] += cl_delay

        # Mask min/max altitude limits so slewtime = np.nan
        outsideLimits = np.where((alt_rad > self.params.telalt_maxpos_rad) |
                                 (alt_rad < self.params.telalt_minpos_rad))
        slewTime[outsideLimits] = -1
        return slewTime

    def configure(self, confdict):
        """Configure the observatory model.

        Parameters
        ----------
        confdict : dict
            The configuration dictionary containing the parameters for
            the observatory model.
        """
        self.configure_telescope(confdict)
        self.configure_rotator(confdict)
        self.configure_dome(confdict)
        self.configure_optics(confdict)
        self.configure_camera(confdict)
        self.configure_slew(confdict)
        self.configure_park(confdict)

        self.current_state.mountedfilters = self.params.filter_init_mounted_list
        self.current_state.unmountedfilters = self.params.filter_init_unmounted_list
        self.park_state.mountedfilters = self.current_state.mountedfilters
        self.park_state.unmountedfilters = self.current_state.unmountedfilters

        self.reset()

    def configure_camera(self, confdict):
        """Configure the camera parameters.

        Parameters
        ----------
        confdict : dict
            The set of configuration parameters for the camera.
        """
        self.params.configure_camera(confdict)

        self.log.log(self.log_level,
                     "configure_camera: filter_changetime=%.1f" %
                     (self.params.filter_changetime))
        self.log.log(self.log_level,
                     "configure_camera: readouttime=%.1f" %
                     (self.params.readouttime))
        self.log.log(self.log_level,
                     "configure_camera: shuttertime=%.1f" %
                     (self.params.shuttertime))
        self.log.log(self.log_level,
                     "configure_camera: filter_removable=%s" %
                     (self.params.filter_removable_list))
        self.log.log(self.log_level,
                     "configure_camera: filter_max_changes_burst_num=%i" %
                     (self.params.filter_max_changes_burst_num))
        self.log.log(self.log_level,
                     "configure_camera: filter_max_changes_burst_time=%.1f" %
                     (self.params.filter_max_changes_burst_time))
        self.log.log(self.log_level,
                     "configure_camera: filter_max_changes_avg_num=%i" %
                     (self.params.filter_max_changes_avg_num))
        self.log.log(self.log_level,
                     "configure_camera: filter_max_changes_avg_time=%.1f" %
                     (self.params.filter_max_changes_avg_time))
        self.log.log(self.log_level,
                     "configure_camera: filter_init_mounted=%s" %
                     (self.params.filter_init_mounted_list))
        self.log.log(self.log_level,
                     "configure_camera: filter_init_unmounted=%s" %
                     (self.params.filter_init_unmounted_list))

    def configure_dome(self, confdict):
        """Configure the dome parameters.

        Parameters
        ----------
        confdict : dict
            The set of configuration parameters for the dome.
        """
        self.params.configure_dome(confdict)

        self.log.log(self.log_level,
                     "configure_dome: domalt_maxspeed=%.3f" %
                     (math.degrees(self.params.domalt_maxspeed_rad)))
        self.log.log(self.log_level,
                     "configure_dome: domalt_accel=%.3f" %
                     (math.degrees(self.params.domalt_accel_rad)))
        self.log.log(self.log_level,
                     "configure_dome: domalt_decel=%.3f" %
                     (math.degrees(self.params.domalt_decel_rad)))
        self.log.log(self.log_level,
                     "configure_dome: domalt_freerange=%.3f" %
                     (math.degrees(self.params.domalt_free_range)))
        self.log.log(self.log_level,
                     "configure_dome: domaz_maxspeed=%.3f" %
                     (math.degrees(self.params.domaz_maxspeed_rad)))
        self.log.log(self.log_level,
                     "configure_dome: domaz_accel=%.3f" %
                     (math.degrees(self.params.domaz_accel_rad)))
        self.log.log(self.log_level,
                     "configure_dome: domaz_decel=%.3f" %
                     (math.degrees(self.params.domaz_decel_rad)))
        self.log.log(self.log_level,
                     "configure_dome: domaz_freerange=%.3f" %
                     (math.degrees(self.params.domaz_free_range)))
        self.log.log(self.log_level,
                     "configure_dome: domaz_settletime=%.3f" %
                     (self.params.domaz_settletime))

    def configure_from_module(self, conf_file=None):
        """Configure the observatory model from the module stored \
           configuration.

        Parameters
        ----------
        conf_file : str, optional
            The configuration file to use.
        """
        if conf_file is None:
            conf_file = os.path.join(os.path.dirname(__file__),
                                     "observatory_model.conf")
        conf_dict = read_conf_file(conf_file)
        self.configure(conf_dict)

    def configure_optics(self, confdict):
        """Configure the optics parameters.

        Parameters
        ----------
        confdict : dict
            The set of configuration parameters for the optics.
        """
        self.params.configure_optics(confdict)

        self.log.log(self.log_level,
                     "configure_optics: optics_ol_slope=%.3f" %
                     (self.params.optics_ol_slope))
        self.log.log(self.log_level,
                     "configure_optics: optics_cl_delay=%s" %
                     (self.params.optics_cl_delay))
        self.log.log(self.log_level,
                     "configure_optics: optics_cl_altlimit=%s" %
                     ([math.degrees(x) for x in self.params.optics_cl_altlimit]))

    def configure_park(self, confdict):
        """Configure the telescope park state parameters.

        Parameters
        ----------
        confdict : dict
            The set of configuration parameters for the telescope park state.
        """
        self.park_state.alt_rad = math.radians(confdict["park"]["telescope_altitude"])
        self.park_state.az_rad = math.radians(confdict["park"]["telescope_azimuth"])
        self.park_state.rot_rad = math.radians(confdict["park"]["telescope_rotator"])
        self.park_state.telalt_rad = math.radians(confdict["park"]["telescope_altitude"])
        self.park_state.telaz_rad = math.radians(confdict["park"]["telescope_azimuth"])
        self.park_state.telrot_rad = math.radians(confdict["park"]["telescope_rotator"])
        self.park_state.domalt_rad = math.radians(confdict["park"]["dome_altitude"])
        self.park_state.domaz_rad = math.radians(confdict["park"]["dome_azimuth"])
        self.park_state.filter = confdict["park"]["filter_position"]
        self.park_state.mountedfilters = self.current_state.mountedfilters
        self.park_state.unmountedfilters = self.current_state.unmountedfilters
        self.park_state.tracking = False

        self.log.log(self.log_level,
                     "configure_park: park_telalt_rad=%.3f" % (self.park_state.telalt_rad))
        self.log.log(self.log_level,
                     "configure_park: park_telaz_rad=%.3f" % (self.park_state.telaz_rad))
        self.log.log(self.log_level,
                     "configure_park: park_telrot_rad=%.3f" % (self.park_state.telrot_rad))
        self.log.log(self.log_level,
                     "configure_park: park_domalt_rad=%.3f" % (self.park_state.domalt_rad))
        self.log.log(self.log_level,
                     "configure_park: park_domaz_rad=%.3f" % (self.park_state.domaz_rad))
        self.log.log(self.log_level,
                     "configure_park: park_filter=%s" % (self.park_state.filter))

    def configure_rotator(self, confdict):
        """Configure the telescope rotator parameters.

        Parameters
        ----------
        confdict : dict
            The set of configuration parameters for the telescope rotator.
        """
        self.params.configure_rotator(confdict)

        self.log.log(self.log_level,
                     "configure_rotator: telrot_minpos=%.3f" %
                     (math.degrees(self.params.telrot_minpos_rad)))
        self.log.log(self.log_level,
                     "configure_rotator: telrot_maxpos=%.3f" %
                     (math.degrees(self.params.telrot_maxpos_rad)))
        self.log.log(self.log_level,
                     "configure_rotator: telrot_maxspeed=%.3f" %
                     (math.degrees(self.params.telrot_maxspeed_rad)))
        self.log.log(self.log_level,
                     "configure_rotator: telrot_accel=%.3f" %
                     (math.degrees(self.params.telrot_accel_rad)))
        self.log.log(self.log_level,
                     "configure_rotator: telrot_decel=%.3f" %
                     (math.degrees(self.params.telrot_decel_rad)))
        self.log.log(self.log_level,
                     "configure_rotator: telrot_filterchangepos=%.3f" %
                     (math.degrees(self.params.telrot_filterchangepos_rad)))
        self.log.log(self.log_level,
                     "configure_rotator: rotator_followsky=%s" %
                     (self.params.rotator_followsky))
        self.log.log(self.log_level,
                     "configure_rotator: rotator_resumeangle=%s" %
                     (self.params.rotator_resumeangle))

    def configure_slew(self, confdict):
        """Configure the slew parameters.

        Parameters
        ----------
        confdict : dict
            The set of configuration parameters for the slew.
        """
        self.params.configure_slew(confdict, self.activities)

        for activity in self.activities:
            self.log.log(self.log_level, "configure_slew: prerequisites[%s]=%s" %
                         (activity, self.params.prerequisites[activity]))

    def configure_telescope(self, confdict):
        """Configure the telescope parameters.

        Parameters
        ----------
        confdict : dict
            The set of configuration parameters for the telescope.
        """
        self.params.configure_telescope(confdict)

        self.log.log(self.log_level,
                     "configure_telescope: telalt_minpos=%.3f" %
                     (math.degrees(self.params.telalt_minpos_rad)))
        self.log.log(self.log_level,
                     "configure_telescope: telalt_maxpos=%.3f" %
                     (math.degrees(self.params.telalt_maxpos_rad)))
        self.log.log(self.log_level,
                     "configure_telescope: telaz_minpos=%.3f" %
                     (math.degrees(self.params.telaz_minpos_rad)))
        self.log.log(self.log_level,
                     "configure_telescope: telaz_maxpos=%.3f" %
                     (math.degrees(self.params.telaz_maxpos_rad)))
        self.log.log(self.log_level,
                     "configure_telescope: telalt_maxspeed=%.3f" %
                     (math.degrees(self.params.telalt_maxspeed_rad)))
        self.log.log(self.log_level,
                     "configure_telescope: telalt_accel=%.3f" %
                     (math.degrees(self.params.telalt_accel_rad)))
        self.log.log(self.log_level,
                     "configure_telescope: telalt_decel=%.3f" %
                     (math.degrees(self.params.telalt_decel_rad)))
        self.log.log(self.log_level,
                     "configure_telescope: telaz_maxspeed=%.3f" %
                     (math.degrees(self.params.telaz_maxspeed_rad)))
        self.log.log(self.log_level,
                     "configure_telescope: telaz_accel=%.3f" %
                     (math.degrees(self.params.telaz_accel_rad)))
        self.log.log(self.log_level,
                     "configure_telescope: telaz_decel=%.3f" %
                     (math.degrees(self.params.telaz_decel_rad)))
        self.log.log(self.log_level,
                     "configure_telescope: mount_settletime=%.3f" %
                     (self.params.mount_settletime))

    def get_closest_angle_distance(self, target_rad, current_abs_rad,
                                   min_abs_rad=None, max_abs_rad=None):
        """Calculate the closest angular distance including handling \
           cable wrap if necessary.

        Parameters
        ----------
        target_rad : float
            The destination angle (radians).
        current_abs_rad : float
            The current angle (radians).
        min_abs_rad : float, optional
            The minimum constraint angle (radians).
        max_abs_rad : float, optional
            The maximum constraint angle (radians).

        Returns
        -------
        tuple(float, float)
            (accumulated angle in radians, distance angle in radians)
        """
        # if there are wrap limits, normalizes the target angle
        if min_abs_rad is not None:
            norm_target_rad = divmod(target_rad - min_abs_rad, TWOPI)[1] + min_abs_rad
            if max_abs_rad is not None:
                # if the target angle is unreachable
                # then sets an arbitrary value
                if norm_target_rad > max_abs_rad:
                    norm_target_rad = max(min_abs_rad, norm_target_rad - math.pi)
        else:
            norm_target_rad = target_rad

        # computes the distance clockwise
        distance_rad = divmod(norm_target_rad - current_abs_rad, TWOPI)[1]

        # take the counter-clockwise distance if shorter
        if distance_rad > math.pi:
            distance_rad = distance_rad - TWOPI

        # if there are wrap limits
        if (min_abs_rad is not None) and (max_abs_rad is not None):
            # compute accumulated angle
            accum_abs_rad = current_abs_rad + distance_rad

            # if limits reached chose the other direction
            if accum_abs_rad > max_abs_rad:
                distance_rad = distance_rad - TWOPI
            if accum_abs_rad < min_abs_rad:
                distance_rad = distance_rad + TWOPI

        # compute final accumulated angle
        final_abs_rad = current_abs_rad + distance_rad

        return (final_abs_rad, distance_rad)

    def get_closest_state(self, targetposition, istracking=False):
        """Find the closest observatory state for the given target position.

        Parameters
        ----------
        targetposition : :class:`.ObservatoryPosition`
            A target position instance.
        istracking : bool, optional
            Flag for saying if the observatory is tracking. Default is False.

        Returns
        -------
        :class:`.ObservatoryState`
            The state that is closest to the current observatory state.

        Binary schema
        -------------
        The binary schema used to determine the state of a proposed target. A
        value of 1 indicates that is it failing. A value of 0 indicates that the
        state is passing.
        ___  ___  ___  ___  ___  ___
         |    |    |    |    |    |
        rot  rot  az   az   alt  alt
        max  min  max  min  max  min

        For example, if a proposed target exceeds the rotators maximum value,
        and is below the minimum azimuth we would have a binary value of;

         0    1    0    1    0    0

        If the target passed, then no limitations would occur;

         0    0    0    0    0    0
        """

        valid_state = True
        fail_record = self.current_state.fail_record
        self.current_state.fail_state = 0

        if targetposition.alt_rad < self.params.telalt_minpos_rad:
            telalt_rad = self.params.telalt_minpos_rad
            domalt_rad = self.params.telalt_minpos_rad
            valid_state = False

            if "telalt_minpos_rad" in fail_record:
                fail_record["telalt_minpos_rad"] += 1
            else:
                fail_record["telalt_minpos_rad"] = 1

            self.current_state.fail_state = self.current_state.fail_state | \
                                            self.current_state.fail_value_table["altEmin"]

        elif targetposition.alt_rad > self.params.telalt_maxpos_rad:
            telalt_rad = self.params.telalt_maxpos_rad
            domalt_rad = self.params.telalt_maxpos_rad
            valid_state = False
            if "telalt_maxpos_rad" in fail_record:
                fail_record["telalt_maxpos_rad"] += 1
            else:
                fail_record["telalt_maxpos_rad"] = 1

            self.current_state.fail_state = self.current_state.fail_state | \
                                            self.current_state.fail_value_table["altEmax"]

        else:
            telalt_rad = targetposition.alt_rad
            domalt_rad = targetposition.alt_rad

        if istracking:
            (telaz_rad, delta) = self.get_closest_angle_distance(targetposition.az_rad,
                                                                 self.current_state.telaz_rad)
            if telaz_rad < self.params.telaz_minpos_rad:
                telaz_rad = self.params.telaz_minpos_rad
                valid_state = False
                if "telaz_minpos_rad" in fail_record:
                    fail_record["telaz_minpos_rad"] += 1
                else:
                    fail_record["telaz_minpos_rad"] = 1

                self.current_state.fail_state = self.current_state.fail_state | \
                                                self.current_state.fail_value_table["azEmin"]

            elif telaz_rad > self.params.telaz_maxpos_rad:
                telaz_rad = self.params.telaz_maxpos_rad
                valid_state = False
                if "telaz_maxpos_rad" in fail_record:
                    fail_record["telaz_maxpos_rad"] += 1
                else:
                    fail_record["telaz_maxpos_rad"] = 1

                self.current_state.fail_state = self.current_state.fail_state | \
                                                self.current_state.fail_value_table["azEmax"]

        else:
            (telaz_rad, delta) = self.get_closest_angle_distance(targetposition.az_rad,
                                                                 self.current_state.telaz_rad,
                                                                 self.params.telaz_minpos_rad,
                                                                 self.params.telaz_maxpos_rad)

        (domaz_rad, delta) = self.get_closest_angle_distance(targetposition.az_rad,
                                                             self.current_state.domaz_rad)

        if istracking:
            (telrot_rad, delta) = self.get_closest_angle_distance(targetposition.rot_rad,
                                                                  self.current_state.telrot_rad)
            if telrot_rad < self.params.telrot_minpos_rad:
                telrot_rad = self.params.telrot_minpos_rad
                valid_state = False
                if "telrot_minpos_rad" in fail_record:
                    fail_record["telrot_minpos_rad"] += 1
                else:
                    fail_record["telrot_minpos_rad"] = 1

                self.current_state.fail_state = self.current_state.fail_state | \
                                                self.current_state.fail_value_table["rotEmin"]

            elif telrot_rad > self.params.telrot_maxpos_rad:
                telrot_rad = self.params.telrot_maxpos_rad
                valid_state = False
                if "telrot_maxpos_rad" in fail_record:
                    fail_record["telrot_maxpos_rad"] += 1
                else:
                    fail_record["telrot_maxpos_rad"] = 1

                self.current_state.fail_state = self.current_state.fail_state | \
                                                self.current_state.fail_value_table["rotEmax"]
        else:
            # if the target rotator angle is unreachable
            # then sets an arbitrary value (opposite)
            norm_rot_rad = divmod(targetposition.rot_rad - self.params.telrot_minpos_rad, TWOPI)[1] \
                + self.params.telrot_minpos_rad
            if norm_rot_rad > self.params.telrot_maxpos_rad:
                targetposition.rot_rad = norm_rot_rad - math.pi
            (telrot_rad, delta) = self.get_closest_angle_distance(targetposition.rot_rad,
                                                                  self.current_state.telrot_rad,
                                                                  self.params.telrot_minpos_rad,
                                                                  self.params.telrot_maxpos_rad)
        targetposition.ang_rad = divmod(targetposition.pa_rad - telrot_rad, TWOPI)[1]

        targetstate = ObservatoryState()
        targetstate.set_position(targetposition)
        targetstate.telalt_rad = telalt_rad
        targetstate.telaz_rad = telaz_rad
        targetstate.telrot_rad = telrot_rad
        targetstate.domalt_rad = domalt_rad
        targetstate.domaz_rad = domaz_rad
        if istracking:
            targetstate.tracking = valid_state

        self.current_state.fail_record = fail_record

        return targetstate

    def get_deep_drilling_time(self, target):
        """Get the observing time for a deep drilling target.

        Parameters
        ----------
        target : :class:`.Target`
            The instance containing the target information.

        Returns
        -------
        float
            The total observation time.
        """
        ddtime = target.dd_exptime + \
            target.dd_exposures * self.params.shuttertime + \
            max(target.dd_exposures - 1, 0) * self.params.readouttime + \
            target.dd_filterchanges * (self.params.filter_changetime - self.params.readouttime)

        return ddtime

    def get_delay_after(self, activity, targetstate, initstate):
        """Calculate slew delay for activity.

        This function calculates the slew delay for a given activity based on
        the requested target state and the current observatory state.

        Parameters
        ----------
        activity : str
            The name of the activity for slew delay calculation.
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.

        Returns
        -------
        float
            The slew delay for the activity.
        """
        activity_delay = self.function_get_delay_for[activity](targetstate, initstate)

        prereq_list = self.params.prerequisites[activity]

        longest_previous_delay = 0.0
        longest_prereq = ""
        for prereq in prereq_list:
            previous_delay = self.get_delay_after(prereq, targetstate, initstate)
            if previous_delay > longest_previous_delay:
                longest_previous_delay = previous_delay
                longest_prereq = prereq
        self.longest_prereq_for[activity] = longest_prereq
        self.delay_for[activity] = activity_delay

        return activity_delay + longest_previous_delay

    def get_delay_for_domalt(self, targetstate, initstate):
        """Calculate slew delay for domalt activity.

        This function calculates the slew delay for the domalt activity
        based on the requested target state and the current observatory
        state.

        Parameters
        ----------
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.

        Returns
        -------
        float
            The slew delay for the domalt activity.
        """
        distance = targetstate.domalt_rad - initstate.domalt_rad
        maxspeed = self.params.domalt_maxspeed_rad
        accel = self.params.domalt_accel_rad
        decel = self.params.domalt_decel_rad
        free_range = self.params.domalt_free_range

        (delay, peakspeed) = self.compute_kinematic_delay(distance, maxspeed, accel, decel, free_range)
        targetstate.domalt_peakspeed_rad = peakspeed

        return delay

    def get_delay_for_domaz(self, targetstate, initstate):
        """Calculate slew delay for domaz activity.

        This function calculates the slew delay for the domaz activity
        based on the requested target state and the current observatory
        state.

        Parameters
        ----------
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.

        Returns
        -------
        float
            The slew delay for the domaz activity.
        """
        distance = targetstate.domaz_rad - initstate.domaz_rad
        maxspeed = self.params.domaz_maxspeed_rad
        accel = self.params.domaz_accel_rad
        decel = self.params.domaz_decel_rad
        free_range = self.params.domaz_free_range

        (delay, peakspeed) = self.compute_kinematic_delay(distance, maxspeed, accel, decel, free_range)
        targetstate.domaz_peakspeed_rad = peakspeed

        return delay

    def get_delay_for_domazsettle(self, targetstate, initstate):
        """Calculate slew delay for domazsettle activity.

        This function calculates the slew delay for the domazsettle activity
        based on the requested target state and the current observatory
        state.

        Parameters
        ----------
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.

        Returns
        -------
        float
            The slew delay for the domazsettle activity.
        """
        distance = abs(targetstate.domaz_rad - initstate.domaz_rad)

        if distance > 1e-6:
            delay = self.params.domaz_settletime
        else:
            delay = 0

        return delay

    def get_delay_for_exposures(self, targetstate, initstate):
        """Calculate slew delay for exposures activity.

        This function calculates the slew delay for the exposures activity
        based on the requested target state and the current observatory
        state.

        Parameters
        ----------
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.

        Returns
        -------
        float
            The slew delay for the exposures activity.
        """
        return 0.0

    def get_delay_for_filter(self, targetstate, initstate):
        """Calculate slew delay for filter activity.

        This function calculates the slew delay for the filter activity
        based on the requested target state and the current observatory
        state.

        Parameters
        ----------
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.

        Returns
        -------
        float
            The slew delay for the filter activity.
        """
        if targetstate.filter != initstate.filter:
            # filter change needed
            delay = self.params.filter_changetime
        else:
            delay = 0.0

        return delay

    def get_delay_for_readout(self, targetstate, initstate):
        """Calculate slew delay for readout activity.

        This function calculates the slew delay for the readout activity
        based on the requested target state and the current observatory
        state.

        Parameters
        ----------
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.

        Returns
        -------
        float
            The slew delay for the readout activity.
        """
        return self.params.readouttime

    def get_delay_for_telalt(self, targetstate, initstate):
        """Calculate slew delay for telalt activity.

        This function calculates the slew delay for the telalt activity
        based on the requested target state and the current observatory
        state.

        Parameters
        ----------
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.

        Returns
        -------
        float
            The slew delay for the telalt activity.
        """
        distance = targetstate.telalt_rad - initstate.telalt_rad
        maxspeed = self.params.telalt_maxspeed_rad
        accel = self.params.telalt_accel_rad
        decel = self.params.telalt_decel_rad

        (delay, peakspeed) = self.compute_kinematic_delay(distance, maxspeed, accel, decel)
        targetstate.telalt_peakspeed_rad = peakspeed

        return delay

    def get_delay_for_telaz(self, targetstate, initstate):
        """Calculate slew delay for telaz activity.

        This function calculates the slew delay for the telaz activity
        based on the requested target state and the current observatory
        state.

        Parameters
        ----------
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.

        Returns
        -------
        float
            The slew delay for the telaz activity.
        """
        distance = targetstate.telaz_rad - initstate.telaz_rad
        maxspeed = self.params.telaz_maxspeed_rad
        accel = self.params.telaz_accel_rad
        decel = self.params.telaz_decel_rad

        (delay, peakspeed) = self.compute_kinematic_delay(distance, maxspeed, accel, decel)
        targetstate.telaz_peakspeed_rad = peakspeed

        return delay

    def get_delay_for_telopticsclosedloop(self, targetstate, initstate):
        """Calculate slew delay for telopticsclosedloop activity.

        This function calculates the slew delay for the telopticsclosedloop
        activity based on the requested target state and the current
        observatory state.

        Parameters
        ----------
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.

        Returns
        -------
        float
            The slew delay for the telopticsclosedloop activity.
        """
        distance = abs(targetstate.telalt_rad - initstate.telalt_rad)

        delay = 0.0
        for k, cl_delay in enumerate(self.params.optics_cl_delay):
            if self.params.optics_cl_altlimit[k] <= distance < self.params.optics_cl_altlimit[k + 1]:
                delay = cl_delay
                break

        return delay

    def get_delay_for_telopticsopenloop(self, targetstate, initstate):
        """Calculate slew delay for telopticsopenloop activity.

        This function calculates the slew delay for the telopticsopenloop
        activity based on the requested target state and the current
        observatory state.

        Parameters
        ----------
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.

        Returns
        -------
        float
            The slew delay for the telopticsopenloop activity.
        """
        distance = abs(targetstate.telalt_rad - initstate.telalt_rad)

        if distance > 1e-6:
            delay = distance * self.params.optics_ol_slope
        else:
            delay = 0

        return delay

    def get_delay_for_telrot(self, targetstate, initstate):
        """Calculate slew delay for telrot activity.

        This function calculates the slew delay for the telrot activity
        based on the requested target state and the current observatory
        state.

        Parameters
        ----------
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.

        Returns
        -------
        float
            The slew delay for the telrot activity.
        """
        distance = targetstate.telrot_rad - initstate.telrot_rad
        maxspeed = self.params.telrot_maxspeed_rad
        accel = self.params.telrot_accel_rad
        decel = self.params.telrot_decel_rad

        (delay, peakspeed) = self.compute_kinematic_delay(distance, maxspeed, accel, decel)
        targetstate.telrot_peakspeed_rad = peakspeed

        return delay

    def get_delay_for_telsettle(self, targetstate, initstate):
        """Calculate slew delay for telsettle activity.

        This function calculates the slew delay for the telsettle activity
        based on the requested target state and the current observatory
        state.

        Parameters
        ----------
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.

        Returns
        -------
        float
            The slew delay for the telsettle activity.
        """
        distance = abs(targetstate.telalt_rad - initstate.telalt_rad) + \
            abs(targetstate.telaz_rad - initstate.telaz_rad)

        if distance > 1e-6:
            delay = self.params.mount_settletime
        else:
            delay = 0

        return delay

    def get_delta_filter_avg(self):
        """The time difference between current time and last filter change \
           for average changes.

        Returns
        -------
        float
        """
        avg_num = self.params.filter_max_changes_avg_num
        if len(self.filter_changes_list) >= avg_num:
            deltatime = self.current_state.time - self.filter_changes_list[-avg_num]
        else:
            deltatime = 0.0
        return deltatime

    def get_delta_filter_burst(self):
        """The time difference between current time and last filter change \
           for burst changes.

        Returns
        -------
        float
        """
        burst_num = self.params.filter_max_changes_burst_num
        if len(self.filter_changes_list) >= burst_num:
            deltatime = self.current_state.time - self.filter_changes_list[-burst_num]
        else:
            deltatime = 0.0
        return deltatime

    def get_delta_last_filterchange(self):
        """Get the time difference for filter changes.

        This function calculates the time difference between the current time
        and the time of the last filter change.

        Returns
        -------
        float
            The time difference.
        """
        if len(self.filter_changes_list) > 0:
            delta = self.current_state.time - self.filter_changes_list[-1]
        else:
            delta = self.current_state.time

        return delta

    def get_number_filter_changes(self):
        """The total number of stored filter changes.

        Returns
        -------
        int
        """
        return len(self.filter_changes_list)

    def get_slew_delay(self, target):
        """Calculate the slew delay based on the given target.

        Parameters
        ----------
        target : :class:`.Target`
            An instance of a target for slew calculation.

        Returns
        -------
        float
            The total slew delay for the target.
        """

        if target.filter != self.current_state.filter:
            # check if filter is possible
            if not self.is_filter_change_allowed_for(target.filter):
                return -1.0, self.current_state.fail_value_table["filter"]

        targetposition = self.radecang2position(self.dateprofile,
                                                target.ra_rad,
                                                target.dec_rad,
                                                target.ang_rad,
                                                target.filter)
        if not self.params.rotator_followsky:
            #override rotator position with current telrot
            targetposition.rot_rad = self.current_state.telrot_rad

        # check if altitude is possible
        if targetposition.alt_rad < self.params.telalt_minpos_rad:
            return -1.0, self.current_state.fail_value_table["altEmin"]
        if targetposition.alt_rad > self.params.telalt_maxpos_rad:
            return -1.0, self.current_state.fail_value_table["altEmax"]

        targetstate = self.get_closest_state(targetposition)
        target.ang_rad = targetstate.ang_rad
        target.alt_rad = targetstate.alt_rad
        target.az_rad = targetstate.az_rad
        target.rot_rad = targetstate.rot_rad
        target.telalt_rad = targetstate.telalt_rad
        target.telaz_rad = targetstate.telaz_rad
        target.telrot_rad = targetstate.telrot_rad

        return self.get_slew_delay_for_state(targetstate, self.current_state, False), 0

    def get_slew_delay_for_state(self, targetstate, initstate, include_slew_data=False):
        """Calculate slew delay for target state from current state.

        Parameters
        ----------
        targetstate : :class:`.ObservatoryState`
            The instance containing the target state.
        initstate : :class:`.ObservatoryState`
            The instance containing the current state of the observatory.
        include_slew_data : bool, optional
            Flag to update lastslew_delays_dict member.

        Returns
        -------
        float
            The slew delay for the target state.
        """
        last_activity = "exposures"
        slew_delay = self.get_delay_after(last_activity, targetstate, initstate)

        self.lastslew_delays_dict = {}
        self.lastslew_criticalpath = []
        if include_slew_data:
            for act in self.activities:
                dt = self.delay_for[act]
                if dt > 0.0:
                    self.lastslew_delays_dict[act] = dt

            activity = last_activity
            while activity != "":
                dt = self.delay_for[activity]
                if dt > 0:
                    self.lastslew_criticalpath.append(activity)
                activity = self.longest_prereq_for[activity]

        return slew_delay

    def is_filter_change_allowed(self):
        """Determine is filter change is allowed due to constraints.

        Returns
        -------
        bool
            True is filter change is allowed, else False.
        """
        burst_num = self.params.filter_max_changes_burst_num
        if len(self.filter_changes_list) >= burst_num:
            deltatime = self.current_state.time - self.filter_changes_list[-burst_num]
            if deltatime >= self.params.filter_max_changes_burst_time:
                # burst time allowed
                avg_num = self.params.filter_max_changes_avg_num
                if len(self.filter_changes_list) >= avg_num:
                    deltatime = self.current_state.time - self.filter_changes_list[-avg_num]
                    if deltatime >= self.params.filter_max_changes_avg_time:
                        # avg time allowed
                        allowed = True
                    else:
                        allowed = False
                else:
                    allowed = True
            else:
                allowed = False
        else:
            allowed = True

        return allowed

    def is_filter_change_allowed_for(self, targetfilter):
        """Determine if filter change is allowed given band filter.

        Parameters
        ----------
        targetfilter : str
            The band filter for the target.

        Returns
        -------
        bool
            True is filter change is allowed, else False.
        """
        if targetfilter in self.current_state.mountedfilters:
            # new filter is mounted
            allowed = self.is_filter_change_allowed()
        else:
            allowed = False
        return allowed

    def observe(self, target):
        """Run the observatory through the observing cadence for the target.

        Parameters
        ----------
        target : :class:`.Target`
            The instance containing the target information for the
            observation.
        """
        self.slew(target)
        visit_time = sum(target.exp_times) + \
            target.num_exp * self.params.shuttertime + \
            max(target.num_exp - 1, 0) * self.params.readouttime
        self.update_state(self.current_state.time + visit_time)

    def park(self):
        """Put the observatory into the park state.
        """
        self.park_state.filter = self.current_state.filter
        slew_delay = self.get_slew_delay_for_state(self.park_state, self.current_state, True)
        self.park_state.time = self.current_state.time + slew_delay
        self.current_state.set(self.park_state)
        self.update_state(self.park_state.time)
        self.park_state.time = 0.0

    def radec2altazpa(self, dateprofile, ra_rad, dec_rad):
        """Converts ra, de coordinates into alt, az for given time.

        Parameters
        ----------
        dateprofile : lsst.ts.dateloc.DateProfile
            Instance containing the time information.
        ra_rad : float
            The right ascension in radians
        dec_rad : float
            The declination in radians

        Returns
        -------
        tuple(float, float, float)
            (altitude in radians, azimuth in radians, parallactic angle in
            radians)
        """
        lst_rad = dateprofile.lst_rad
        ha_rad = lst_rad - ra_rad

        (az_rad, alt_rad) = pal.de2h(ha_rad, dec_rad, self.location.latitude_rad)
        pa_rad = divmod(pal.pa(ha_rad, dec_rad, self.location.latitude_rad), TWOPI)[1]

        return (alt_rad, az_rad, pa_rad)

    def radecang2position(self, dateprofile, ra_rad, dec_rad, ang_rad, band_filter):
        """Convert current time, sky location and filter into observatory\
           position.

        Parameters
        ----------
        dateprofile : lsst.ts.dateloc.DateProfile
            The instance holding the current time information.
        ra_rad : float
            The current right ascension (radians).
        dec_rad : float
            The current declination (radians).
        ang_rad : float
            The current sky angle (radians).
        band_filter : str
            The current band filter.

        Returns
        -------
        :class:`.ObservatoryPosition`
            The observatory position information from inputs.
        """
        (alt_rad, az_rad, pa_rad) = self.radec2altazpa(dateprofile, ra_rad, dec_rad)

        position = ObservatoryPosition()
        position.time = dateprofile.timestamp
        position.tracking = True
        position.ra_rad = ra_rad
        position.dec_rad = dec_rad
        position.ang_rad = ang_rad
        position.filter = band_filter
        position.alt_rad = alt_rad
        position.az_rad = az_rad
        position.pa_rad = pa_rad
        position.rot_rad = divmod(pa_rad - ang_rad, TWOPI)[1]

        return position

    def reset(self):
        """Reset the observatory to the parking state.
        """
        self.set_state(self.park_state)

    def set_state(self, new_state):
        """Set observatory state from another state.

        Parameters
        ----------
        new_state : :class:`.ObservatoryState`
            The instance containing the state to update the observatory to.
        """
        if new_state.filter != self.current_state.filter:
            self.filter_changes_list.append(new_state.time)

        self.current_state.set(new_state)
        self.dateprofile.update(new_state.time)

    def slew(self, target):
        """Slew the observatory to the given target location.

        Parameters
        ----------
        target : :class:`.Target`
            The instance containing the target information for the slew.
        """
        self.slew_radec(self.current_state.time,
                        target.ra_rad, target.dec_rad, target.ang_rad, target.filter)

    def slew_altaz(self, time, alt_rad, az_rad, rot_rad, band_filter):
        """Slew observatory to the given alt, az location.

        Parameters
        ----------
        time : float
            The UTC timestamp of the request.
        alt_rad : float
            The altitude (radians) to slew to.
        az_rad : float
            The azimuth (radians) to slew to.
        rot_rad : float
            The telescope rotator angle (radians) for the slew.
        band_filter : str
            The band filter for the slew.
        """
        self.update_state(time)
        time = self.current_state.time

        targetposition = ObservatoryPosition()
        targetposition.time = time
        targetposition.tracking = False
        targetposition.alt_rad = alt_rad
        targetposition.az_rad = az_rad
        targetposition.rot_rad = rot_rad
        targetposition.filter = band_filter

        self.slew_to_position(targetposition)

    def slew_radec(self, time, ra_rad, dec_rad, ang_rad, filter):
        """Slew observatory to the given ra, dec location.

        Parameters
        ----------
        time : float
            The UTC timestamp of the request.
        ra_rad : float
            The right ascension (radians) to slew to.
        dec_rad : float
            The declination (radians) to slew to.
        ang_rad : float
            The sky angle (radians) for the slew.
        band_filter : str
            The band filter for the slew.
        """
        self.update_state(time)
        time = self.current_state.time

        targetposition = self.radecang2position(self.dateprofile, ra_rad, dec_rad, ang_rad, filter)
        if not self.params.rotator_followsky:
            targetposition.rot_rad = self.current_state.telrot_rad

        self.slew_to_position(targetposition)

    def slew_to_position(self, targetposition):
        """Slew the observatory to a given position.

        Parameters
        ----------
        targetposition : :class:`.ObservatoryPosition`
            The instance containing the slew position information.
        """
        targetstate = self.get_closest_state(targetposition)
        targetstate.mountedfilters = self.current_state.mountedfilters
        targetstate.unmountedfilters = self.current_state.unmountedfilters
        slew_delay = self.get_slew_delay_for_state(targetstate, self.current_state, True)
        if targetposition.filter != self.current_state.filter:
            self.filter_changes_list.append(targetstate.time)
        targetstate.time = targetstate.time + slew_delay
        self.current_state.set(targetstate)
        self.update_state(targetstate.time)

    def start_tracking(self, time):
        """Put observatory into tracking mode.

        Parameters
        ----------
        time : float
            The UTC timestamp.
        """
        if time < self.current_state.time:
            time = self.current_state.time
        if not self.current_state.tracking:
            self.update_state(time)
            self.current_state.tracking = True

    def stop_tracking(self, time):
        """Remove observatory from tracking mode.

        Parameters
        ----------
        time : float
            The UTC timestamp.
        """
        if time < self.current_state.time:
            time = self.current_state.time
        if self.current_state.tracking:
            self.update_state(time)
            self.current_state.tracking = False

    def swap_filter(self, filter_to_unmount):
        """Perform a filter swap with the given filter.

        Parameters
        ----------
        filter_to_unmount : str
            The band filter name to unmount.
        """
        if filter_to_unmount in self.current_state.mountedfilters:
            self.current_state.mountedfilters.remove(filter_to_unmount)
            filter_to_mount = self.current_state.unmountedfilters.pop()
            self.current_state.mountedfilters.append(filter_to_mount)
            self.current_state.unmountedfilters.append(filter_to_unmount)

            self.park_state.mountedfilters = self.current_state.mountedfilters
            self.park_state.unmountedfilters = self.current_state.unmountedfilters
        else:
            self.log.info("swap_filter: REJECTED filter %s is not mounted" %
                          (filter_to_unmount))

    def update_state(self, time):
        """Update the observatory state for the given time.

        Parameters
        ----------
        time : float
            A UTC timestamp for updating the observatory state.
        """
        if time < self.current_state.time:
            time = self.current_state.time
        self.dateprofile.update(time)

        if self.current_state.tracking:

            targetposition = self.radecang2position(self.dateprofile,
                                                    self.current_state.ra_rad,
                                                    self.current_state.dec_rad,
                                                    self.current_state.ang_rad,
                                                    self.current_state.filter)

            targetstate = self.get_closest_state(targetposition, istracking=True)

            self.current_state.time = targetstate.time
            self.current_state.alt_rad = targetstate.alt_rad
            self.current_state.az_rad = targetstate.az_rad
            self.current_state.pa_rad = targetstate.pa_rad
            self.current_state.rot_rad = targetstate.rot_rad
            self.current_state.tracking = targetstate.tracking

            self.current_state.telalt_rad = targetstate.telalt_rad
            self.current_state.telaz_rad = targetstate.telaz_rad
            self.current_state.telrot_rad = targetstate.telrot_rad
            self.current_state.domalt_rad = targetstate.domalt_rad
            self.current_state.domaz_rad = targetstate.domaz_rad
        else:
            (ra_rad, dec_rad, pa_rad) = self.altaz2radecpa(self.dateprofile,
                                                           self.current_state.alt_rad,
                                                           self.current_state.az_rad)
            self.current_state.time = time
            self.current_state.ra_rad = ra_rad
            self.current_state.dec_rad = dec_rad
            self.current_state.ang_rad = divmod(pa_rad - self.current_state.rot_rad, TWOPI)[1]
            self.current_state.pa_rad = pa_rad
