import logging
import math
import os

import palpy as pal

from lsst.ts.dateloc import DateProfile, ObservatoryLocation
from lsst.ts.observatory.model import ObservatoryModelParameters
from lsst.ts.observatory.model import ObservatoryPosition
from lsst.ts.observatory.model import ObservatoryState
from lsst.ts.observatory.model import compare, read_conf_file

__all__ = ["ObservatoryModel"]

TWOPI = 2 * math.pi

class ObservatoryModel(object):
    """Class for modelling the observatory.
    """

    def __init__(self, location=None, log_level=logging.DEBUG):
        """Initialize the class.

        Parameters
        ----------
        location : :class:`.ObservatoryLocation`, optional
            An instance of the observatory location. Default is None,
            but this sets up the LSST as the location.
        log_level : int
            Set the logging level for the class. Default is logging.DEBUG.
        """
        self.log = logging.getLogger("observatoryModel")
        self.log_level = log_level

        self.params = ObservatoryModelParameters()
        if location is None:
            self.location = ObservatoryLocation()
            self.location.for_lsst()
        else:
            self.location = location
        self.park_state = ObservatoryState()
        self.current_state = ObservatoryState()
        self.targetPosition = ObservatoryPosition()

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

    def configure_from_module(self, conf_file=None):
        """Configure the observatory model from the module stored
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
                     "configure_dome: domaz_maxspeed=%.3f" %
                     (math.degrees(self.params.domaz_maxspeed_rad)))
        self.log.log(self.log_level,
                     "configure_dome: domaz_accel=%.3f" %
                     (math.degrees(self.params.domaz_accel_rad)))
        self.log.log(self.log_level,
                     "configure_dome: domaz_decel=%.3f" %
                     (math.degrees(self.params.domaz_decel_rad)))
        self.log.log(self.log_level,
                     "configure_dome: domaz_settletime=%.3f" %
                     (self.params.domaz_settletime))

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
                     (self.params.optics_cl_altlimit))

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

    def set_state(self, new_state):
        """Set observatory state from another state.

        Parameters
        ----------
        new_state : :class:`.ObservatoryState`
        """
        if new_state.filter != self.current_state.filter:
            self.filter_changes_list.append(new_state.time)

        self.current_state.set(new_state)
        self.dateprofile.update(new_state.time)

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

    def get_slew_delay(self, target):

        if target.filter != self.current_state.filter:
            # check if filter is possible
            if not self.is_filter_change_allowed_for(target.filter):
                return -1.0

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
            return -1.0
        if targetposition.alt_rad > self.params.telalt_maxpos_rad:
            return -1.0

        targetstate = self.get_closest_state(targetposition)
        target.ang_rad = targetstate.ang_rad
        target.alt_rad = targetstate.alt_rad
        target.az_rad = targetstate.az_rad
        target.rot_rad = targetstate.rot_rad
        target.telalt_rad = targetstate.telalt_rad
        target.telaz_rad = targetstate.telaz_rad
        target.telrot_rad = targetstate.telrot_rad

        return self.get_slew_delay_for_state(targetstate, self.current_state, False)

    def get_closest_state(self, targetposition, istracking=False):

        valid_state = True

        if targetposition.alt_rad < self.params.telalt_minpos_rad:
            telalt_rad = self.params.telalt_minpos_rad
            domalt_rad = self.params.telalt_minpos_rad
            valid_state = False
        elif targetposition.alt_rad > self.params.telalt_maxpos_rad:
            telalt_rad = self.params.telalt_maxpos_rad
            domalt_rad = self.params.telalt_maxpos_rad
            valid_state = False
        else:
            telalt_rad = targetposition.alt_rad
            domalt_rad = targetposition.alt_rad

        if istracking:
            (telaz_rad, delta) = self.get_closest_angle_distance(targetposition.az_rad,
                                                                 self.current_state.telaz_rad)
            if telaz_rad < self.params.telaz_minpos_rad:
                telaz_rad = self.params.telaz_minpos_rad
                valid_state = False
            elif telaz_rad > self.params.telaz_maxpos_rad:
                telaz_rad = self.params.telaz_maxpos_rad
                valid_state = False
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
            elif telrot_rad > self.params.telrot_maxpos_rad:
                telrot_rad = self.params.telrot_maxpos_rad
                valid_state = False
        else:
            # if the target rotator angle is unreachable
            # then sets an arbitrary value (oposite)
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

        return targetstate

    def get_closest_angle_distance(self, target_rad, current_abs_rad, min_abs_rad=None, max_abs_rad=None):

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

    def radecang2position(self, dateprofile, ra_rad, dec_rad, ang_rad, filter):

        (alt_rad, az_rad, pa_rad) = self.radec2altazpa(dateprofile, ra_rad, dec_rad)

        position = ObservatoryPosition()
        position.time = dateprofile.timestamp
        position.tracking = True
        position.ra_rad = ra_rad
        position.dec_rad = dec_rad
        position.ang_rad = ang_rad
        position.filter = filter
        position.alt_rad = alt_rad
        position.az_rad = az_rad
        position.pa_rad = pa_rad
        position.rot_rad = divmod(pa_rad - ang_rad, TWOPI)[1]

        return position

    def radec2altazpa(self, dateprofile, ra_rad, dec_rad):
        """
        Converts ra_rad, dec_rad coordinates into alt_rad az_rad for given DATE.
        inputs:
               ra_rad:  Right Ascension in radians
               dec_rad: Declination in radians
               DATE: Time in seconds since simulation reference (SIMEPOCH)
        output:
               (alt_rad, az_rad, pa_rad, HA_HOU)
               alt_rad: Altitude in radians [-90.0  90.0] 90=>zenith
               az_rad:  Azimuth in radians [  0.0 360.0] 0=>N 90=>E
               pa_rad:  Parallactic Angle in radians
               HA_HOU:  Hour Angle in hours
        """
        lst_rad = dateprofile.lst_rad
        ha_rad = lst_rad - ra_rad

        (az_rad, alt_rad) = pal.de2h(ha_rad, dec_rad, self.location.latitude_rad)
        pa_rad = divmod(pal.pa(ha_rad, dec_rad, self.location.latitude_rad), TWOPI)[1]

        return (alt_rad, az_rad, pa_rad)

    def start_tracking(self, time):
        if time < self.current_state.time:
            time = self.current_state.time
        if not self.current_state.tracking:
            self.update_state(time)
            self.current_state.tracking = True

    def stop_tracking(self, time):
        if time < self.current_state.time:
            time = self.current_state.time
        if self.current_state.tracking:
            self.update_state(time)
            self.current_state.tracking = False

    def slew_altaz(self, time, alt_rad, az_rad, rot_rad, filter):

        self.update_state(time)
        time = self.current_state.time

        targetposition = ObservatoryPosition()
        targetposition.time = time
        targetposition.tracking = False
        targetposition.alt_rad = alt_rad
        targetposition.az_rad = az_rad
        targetposition.rot_rad = rot_rad
        targetposition.filter = filter

        self.slew_to_position(targetposition)

    def slew_radec(self, time, ra_rad, dec_rad, ang_rad, filter):

        self.update_state(time)
        time = self.current_state.time

        targetposition = self.radecang2position(self.dateprofile, ra_rad, dec_rad, ang_rad, filter)
        if not self.params.rotator_followsky:
            targetposition.rot_rad = self.current_state.telrot_rad

        self.slew_to_position(targetposition)

    def slew(self, target):

        self.slew_radec(self.current_state.time,
                        target.ra_rad, target.dec_rad, target.ang_rad, target.filter)

    def observe(self, target):

        self.slew(target)
        visit_time = sum(target.exp_times) + \
            target.num_exp * self.params.shuttertime + \
            max(target.num_exp - 1, 0) * self.params.readouttime
        self.update_state(self.current_state.time + visit_time)

    def get_deep_drilling_time(self, target):

        ddtime = target.dd_exptime + \
            target.dd_exposures * self.params.shuttertime + \
            max(target.dd_exposures - 1, 0) * self.params.readouttime + \
            target.dd_filterchanges * (self.params.filter_changetime - self.params.readouttime)

        return ddtime

    def park(self):

        self.park_state.filter = self.current_state.filter
        slew_delay = self.get_slew_delay_for_state(self.park_state, self.current_state, True)
        self.park_state.time = self.current_state.time + slew_delay
        self.current_state.set(self.park_state)
        self.update_state(self.park_state.time)
        self.park_state.time = 0.0

    def swap_filter(self, filter_to_unmount):

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

    def slew_to_position(self, targetposition):

        targetstate = self.get_closest_state(targetposition)
        targetstate.mountedfilters = self.current_state.mountedfilters
        targetstate.unmountedfilters = self.current_state.unmountedfilters
        slew_delay = self.get_slew_delay_for_state(targetstate, self.current_state, True)
        if targetposition.filter != self.current_state.filter:
            self.filter_changes_list.append(targetstate.time)
        targetstate.time = targetstate.time + slew_delay
        self.current_state.set(targetstate)
        self.update_state(targetstate.time)

    def reset(self):

        self.set_state(self.park_state)

    def compute_kinematic_delay(self, distance, maxspeed, accel, decel):

        d = abs(distance)

        vpeak = (2 * d / (1 / accel + 1 / decel)) ** 0.5
        if vpeak <= maxspeed:
            delay = vpeak / accel + vpeak / decel
        else:
            d1 = 0.5 * (maxspeed * maxspeed) / accel
            d3 = 0.5 * (maxspeed * maxspeed) / decel
            d2 = d - d1 - d3

            t1 = maxspeed / accel
            t3 = maxspeed / decel
            t2 = d2 / maxspeed

            delay = t1 + t2 + t3
            vpeak = maxspeed

        return (delay, vpeak * compare(distance, 0))

    def get_slew_delay_for_state(self, targetstate, initstate, include_slew_data=False):

        last_activity = "exposures"
        slew_delay = self.get_delay_after(last_activity, targetstate, initstate)

        self.lastslew_delays_dict = {}
        self.lastslew_criticalpath = []
        if include_slew_data:
            for act in self.activities:
                self.lastslew_delays_dict[act] = self.delay_for[act]

            activity = last_activity
            while activity != "":
                dt = self.delay_for[activity]
                if dt > 0:
                    self.lastslew_criticalpath.append(activity)
                activity = self.longest_prereq_for[activity]

        return slew_delay

    def get_delay_after(self, activity, targetstate, initstate):

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

    def get_delay_for_telalt(self, targetstate, initstate):

        distance = targetstate.telalt_rad - initstate.telalt_rad
        maxspeed = self.params.telalt_maxspeed_rad
        accel = self.params.telalt_accel_rad
        decel = self.params.telalt_decel_rad

        (delay, peakspeed) = self.compute_kinematic_delay(distance, maxspeed, accel, decel)
        targetstate.telalt_peakspeed_rad = peakspeed

        return delay

    def get_delay_for_telaz(self, targetstate, initstate):

        distance = targetstate.telaz_rad - initstate.telaz_rad
        maxspeed = self.params.telaz_maxspeed_rad
        accel = self.params.telaz_accel_rad
        decel = self.params.telaz_decel_rad

        (delay, peakspeed) = self.compute_kinematic_delay(distance, maxspeed, accel, decel)
        targetstate.telaz_peakspeed_rad = peakspeed

        return delay

    def get_delay_for_telrot(self, targetstate, initstate):

        distance = targetstate.telrot_rad - initstate.telrot_rad
        maxspeed = self.params.telrot_maxspeed_rad
        accel = self.params.telrot_accel_rad
        decel = self.params.telrot_decel_rad

        (delay, peakspeed) = self.compute_kinematic_delay(distance, maxspeed, accel, decel)
        targetstate.telrot_peakspeed_rad = peakspeed

        return delay

    def get_delay_for_telsettle(self, targetstate, initstate):

        distance = abs(targetstate.telalt_rad - initstate.telalt_rad) + \
            abs(targetstate.telaz_rad - initstate.telaz_rad)

        if distance > 1e-6:
            delay = self.params.mount_settletime
        else:
            delay = 0

        return delay

    def get_delay_for_telopticsopenloop(self, targetstate, initstate):

        distance = abs(targetstate.telalt_rad - initstate.telalt_rad)

        if distance > 1e-6:
            delay = distance * self.params.optics_ol_slope
        else:
            delay = 0

        return delay

    def get_delay_for_telopticsclosedloop(self, targetstate, initstate):

        distance = abs(targetstate.telalt_rad - initstate.telalt_rad)

        delay = 0.0
        for k, cl_delay in enumerate(self.params.optics_cl_delay):
            if self.params.optics_cl_altlimit[k] <= distance < self.params.optics_cl_altlimit[k + 1]:
                delay = cl_delay
                break

        return delay

    def get_delay_for_domalt(self, targetstate, initstate):

        distance = targetstate.domalt_rad - initstate.domalt_rad
        maxspeed = self.params.domalt_maxspeed_rad
        accel = self.params.domalt_accel_rad
        decel = self.params.domalt_decel_rad

        (delay, peakspeed) = self.compute_kinematic_delay(distance, maxspeed, accel, decel)
        targetstate.domalt_peakspeed_rad = peakspeed

        return delay

    def get_delay_for_domaz(self, targetstate, initstate):

        distance = targetstate.domaz_rad - initstate.domaz_rad
        maxspeed = self.params.domaz_maxspeed_rad
        accel = self.params.domaz_accel_rad
        decel = self.params.domaz_decel_rad

        (delay, peakspeed) = self.compute_kinematic_delay(distance, maxspeed, accel, decel)
        targetstate.domaz_peakspeed_rad = peakspeed

        return delay

    def get_delay_for_domazsettle(self, targetstate, initstate):

        distance = abs(targetstate.domaz_rad - initstate.domaz_rad)

        if distance > 1e-6:
            delay = self.params.domaz_settletime
        else:
            delay = 0

        return delay

    def is_filter_change_allowed_for(self, targetfilter):

        if targetfilter in self.current_state.mountedfilters:
            # new filter is mounted
            allowed = self.is_filter_change_allowed()
        else:
            allowed = False
        return allowed

    def is_filter_change_allowed(self):

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

    def get_delta_last_filterchange(self):

        if len(self.filter_changes_list) > 0:
            delta = self.current_state.time - self.filter_changes_list[-1]
        else:
            delta = self.current_state.time

        return delta

    def get_delay_for_filter(self, targetstate, initstate):

        if targetstate.filter != initstate.filter:
            # filter change needed
            delay = self.params.filter_changetime
        else:
            delay = 0.0

        return delay

    def get_number_filter_changes(self):
        return len(self.filter_changes_list)

    def get_delta_filter_burst(self):
        burst_num = self.params.filter_max_changes_burst_num
        if len(self.filter_changes_list) >= burst_num:
            deltatime = self.current_state.time - self.filter_changes_list[-burst_num]
        else:
            deltatime = 0.0
        return deltatime

    def get_delta_filter_avg(self):
        avg_num = self.params.filter_max_changes_avg_num
        if len(self.filter_changes_list) >= avg_num:
            deltatime = self.current_state.time - self.filter_changes_list[-avg_num]
        else:
            deltatime = 0.0
        return deltatime

    def get_delay_for_readout(self, targetstate, initstate):

        return self.params.readouttime

    def get_delay_for_exposures(self, targetstate, initstate):

        return 0.0

    def altaz2radecpa(self, dateprofile, alt_rad, az_rad):
        """Converts ALT, AZ coordinates into RA, DEC for the given TIME.

        Parameters
        ----------
        dateprofile : :class:`.DateProfile`
            Instance containing the time information.
        alt_rad : float
            Altitude in radians [-90.0deg  90.0deg] 90deg=>zenith
        az_rad : float
            Azimuth in radians [0.0deg 360.0deg] 0deg=>N 90deg=>E

        Returns
        -------
        tuple(float, float)
            (Right Ascension in radians, Declination in radians)
        """
        lst_rad = dateprofile.lst_rad

        (ha_rad, dec_rad) = pal.dh2e(az_rad, alt_rad, self.location.latitude_rad)
        pa_rad = divmod(pal.pa(ha_rad, dec_rad, self.location.latitude_rad), TWOPI)[1]
        ra_rad = divmod(lst_rad - ha_rad, TWOPI)[1]

        return (ra_rad, dec_rad, pa_rad)
