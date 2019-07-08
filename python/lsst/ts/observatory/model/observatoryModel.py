import logging
import warnings
import math
import numpy as np
from astropy.time import TimeDelta
from .observatoryModelConfig import Config
from .utils import get_closest_angle_distance
from lsst.ts.observatory.model import ObservatoryPosition, ObservatoryState

warnings.filterwarnings("ignore",
                        message='.*taiutc.*dubious.year.*')


__all__ = ["ObservatoryModel"]


TWOPI = 2 * np.pi


class ObservatoryModel(object):
    """Class for modeling the observatory.

    Parameters
    ----------
    time: astropy.time.Time
        Time for the initial telescope state.
    config: ~lsst.ts.observatory.model.Config
        Default (none) will use default values of the configuration.
    log_level : int
        Set the logging level for the class. Default is logging.DEBUG.
    """
    def __init__(self, time, config=None, log_level=logging.DEBUG):

        self.log = logging.getLogger("ObservatoryModel")
        self.log_level = log_level
        self.time = time
        self.configure(config)

        self.filters = ["u", "g", "r", "i", "z", "y"]

        # Define activities and summarize prerequisites for each activity.
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
        # Define general prereqs for each activity.
        # Use the fact that the slew config defines all prereqs for all activities.
        self.prerequisites = {}
        for activity, prereq in self.conf.slew.iteritems():
            act = activity.split('_')[1]
            self.prerequisites[act] = prereq
        # Check all activities listed.
        for activity in self.activities:
            if activity not in self.prerequisites:
                raise ValueError('Missing activity %s from slew config' % activity)
        # Define functions, delay, and longest_preqreq for each activity.
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

    def configure(self, config=None):
        """Configure the model. After 'configure' the model config will be frozen.

        Configure basically resets the telescope model to the initial state (which filters are mounted, etc.)
        then puts the telescope at park, and updates the state (to get an accurate ra/dec value).
        Note though that the time is set to self.time, which may not be the original start time.

        Parameters
        ----------
        config: ~lsst.ts.observatory.model.Config
        """
        if config is None:
            self.conf = Config()
        else:
            self.conf = config
        self.conf.validate()
        self.conf.freeze()
        self.site = self.conf.site
        self.siteUtils = self.conf.siteUtils

        # Set the 'current' state (to defaults, except for filters and time)
        self.current_state = ObservatoryState(self.time)
        self.current_state.mountedfilters = list(self.conf.camera.filters_mounted)
        self.current_state.unmountedfilters = list(self.conf.camera.filters_unmounted)
        # Set the 'park' state
        self.configure_park()
        # Set the telescope to the park state.
        self.reset()
        # And set the ra/dec values
        self.update_state()

    def configure_park(self):
        """Configure the telescope park state parameters.

        Parameters
        ----------
        confdict : dict
            The set of configuration parameters for the telescope park state.
        """
        # filterband for the park state is the filter that should be in place during a filter change.
        self.park_state = ObservatoryState(time = self.current_state.time,
                                           alt_rad = math.radians(self.conf.park.telescope_altitude),
                                           az_rad = math.radians(self.conf.park.telescope_azimuth),
                                           rot_rad = math.radians(self.conf.park.telescope_rotator),
                                           telalt_rad = math.radians(self.conf.park.telescope_altitude),
                                           telaz_rad = math.radians(self.conf.park.telescope_azimuth),
                                           telrot_rad = math.radians(self.conf.park.telescope_rotator),
                                           domalt_rad = math.radians(self.conf.park.dome_altitude),
                                           domaz_rad = math.radians(self.conf.park.dome_azimuth),
                                           filterband = self.conf.park.filter_position,
                                           mountedfilters = self.current_state.mountedfilters,
                                           unmountedfilters = self.current_state.unmountedfilters,
                                           tracking=False)
        self.log.log(self.log_level, "Configured park: %s" % (self.park_state))

    def config_info(self):
        """Report configuration parameters and version information.

        Returns
        -------
        OrderedDict
        """
        return self.conf.config_info()

    def __call__(self, efdData, targetDict):
        """Return the current state of the observatory. Ideally, called at the end of an exposure.
        If given a targetmap in alt/az/filter as part of the targetDict, will also
        return the approximate slew delay for these values.

        Note that there should be some thought spent here about the observatory model in simulations
        vs in operations. In particular, the delay between when targets are requested/set in the queue
        compared to when they are executed should be taken into consideration for use.

        There is also some inconsistency here with other "Models" .. here the ObservatoryModel both
        predicts how the observatory will move/behave, and is also simulating the actual behavior of the
        telescope. This is reflected in that the ObservatoryModel tracks time and state, and also
        predicts slew times. It may make sense to split this Model into the approximate slew delay estimates
        and then a separate "Simulated" or "Acting" Observatory model.

        Parameters
        ----------
        efdData: dict
            Dictionary of input telemetry, typically from the EFD.
            This must contain columns self.efd_requirements.
            (work in progress on handling time history).
        targetDict: dict
            Dictionary of target map values over which to calculate the processed telemetry.
            (e.g. targetDict = {'ra': [], 'dec': [], 'altitude': [], 'azimuth': [], 'airmass': []})
            Here we use 'altitude' and 'azimuth', which should be numpy arrays .

        Returns
        -------
        dict of ObservatoryState, nd.array
            ObservatoryState and an array of slewtimes to the alt/az/filter values.
        """
        self.update_state(efdData['time'])
        if 'altitude' in targetDict and 'azimuth' in targetDict and 'filter' in targetDict:
            approximate_slew_delays = self.get_approximate_slew_delay(targetDict['altitude'],
                                                                      targetDict['azimuth'],
                                                                      targetDict['filter'],
                                                                      lax_dome=True)
        else:
            approximate_slew_delays = None
        return {'state': self.current_state, 'slew_delays': approximate_slew_delays}

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
        deltaAz = np.divmod(az_rad - self.current_state.az_rad, TWOPI)[1]
        get_shorter = np.where(deltaAz > np.pi)
        deltaAz[get_shorter] -= TWOPI
        deltaAz = np.abs(deltaAz)

        # Calculate how long the telescope will take to slew to this position with cable wrap on azimuth
        current_abs_rad = self.current_state.telaz_rad
        max_abs_rad = self.conf.telrad['azimuth_maxpos_rad']
        min_abs_rad = self.conf.telrad['azimuth_minpos_rad']

        norm_az_rad = np.divmod(az_rad - min_abs_rad, TWOPI)[1] + min_abs_rad
        if type(norm_az_rad) is float and norm_az_rad > max_abs_rad:
            norm_az_rad = max(min_abs_rad, norm_az_rad - math.pi)
        else:
            out_of_bounds = np.where(norm_az_rad > max_abs_rad)
            to_compare = np.zeros(np.size(out_of_bounds[0]))+min_abs_rad
            norm_az_rad[out_of_bounds] = np.maximum(to_compare, norm_az_rad[out_of_bounds] - np.pi)

        # computes the distance clockwise
        distance_rad = divmod(norm_az_rad - current_abs_rad, TWOPI)[1]
        get_shorter = np.where(distance_rad > np.pi)
        distance_rad[get_shorter] -= TWOPI
        accum_abs_rad = current_abs_rad + distance_rad

        mask_max = np.where(accum_abs_rad > max_abs_rad)
        mask_min = np.where(accum_abs_rad < min_abs_rad)
        distance_rad[mask_max] -= TWOPI
        distance_rad[mask_min] += TWOPI

        telAltSlewTime = self._uamSlewTime(deltaAlt, self.conf.telrad['altitude_maxspeed_rad'],
                                           self.conf.telrad['altitude_accel_rad'])
        telAzSlewTime = self._uamSlewTime(np.abs(distance_rad), self.conf.telrad['azimuth_maxspeed_rad'],
                                          self.conf.telrad['azimuth_accel_rad'])
        totTelTime = np.maximum(telAltSlewTime, telAzSlewTime)

        # Time for open loop optics correction
        olTime = deltaAlt / self.conf.opticsrad['tel_optics_ol_slope_rad']
        totTelTime += olTime
        # Add time for telescope settle.
        settleAndOL = np.where(totTelTime > 0)
        totTelTime[settleAndOL] += np.maximum(0, self.conf.telescope.settle_time - olTime[settleAndOL])
        # And readout puts a floor on tel time
        totTelTime = np.maximum(self.conf.camera.readout_time, totTelTime)

        # now compute dome slew time
        if lax_dome:
            # REPLACE THIS -- should use the free range parameter.
            totDomeTime = np.zeros(len(alt_rad), float)
            # model dome creep, dome slit, and no azimuth settle
            # if we can fit both exposures in the dome slit, do so
            sameDome = np.where(deltaAlt ** 2 + deltaAz ** 2 < self.conf.camera.camera_fov ** 2)

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
            domSlitDiam = self.conf.camera.camera_fov / 2.0
            domDeltaAz = deltaAz - 2 * (domSlitDiam / 2 - self.conf.camera.camera_fov / 2)
            domAltSlewTime = domDeltaAlt / self.conf.domerad['altitude_maxspeed_rad']
            domAzSlewTime = domDeltaAz / self.conf.domerad['azimuth_maxspeed_rad']
            totDomTime1 = np.maximum(domAltSlewTime, domAzSlewTime)

            domDeltaAlt = deltaAlt - 2 * (domSlitDiam / 2 - self.conf.camera.camera_fov / 2)
            domDeltaAz = deltaAz
            domAltSlewTime = domDeltaAlt / self.conf.domerad['altitude_maxspeed_rad']
            domAzSlewTime = domDeltaAz / self.conf.domerad['azimuth_maxspeed_rad']
            totDomTime2 = np.maximum(domAltSlewTime, domAzSlewTime)

            totDomTime = np.minimum(totDomTime1, totDomTime2)
            totDomTime[sameDome] = 0

        else:
            # the above models a dome slit and dome creep. However, it appears that
            # SOCS requires the dome to slew exactly to each field and settle in az
            domAltSlewTime = self._uamSlewTime(deltaAlt,
                                               self.conf.domerad['altitude_maxspeed_rad'],
                                               self.conf.domerad['altitude_accel_rad'])
            domAzSlewTime = self._uamSlewTime(deltaAz, self.conf.domerad['azimuth_maxspeed_rad'],
                                              self.conf.domerad['azimuth_accel_rad'])
            # Dome takes 1 second to settle in az
            domAzSlewTime = np.where(domAzSlewTime > 0,
                                     domAzSlewTime + self.conf.dome.settle_time,
                                     domAzSlewTime)
            totDomTime = np.maximum(domAltSlewTime, domAzSlewTime)
        # Find the max of the above for slew time.
        slewTime = np.maximum(totTelTime, totDomTime)
        # include filter change time if necessary
        filterChange = np.where(goal_filter != self.current_state.filterband)
        slewTime[filterChange] = np.maximum(slewTime[filterChange],
                                            self.conf.camera.filter_change_time)
        # Add closed loop optics correction
        # Find the limit where we must add the delay
        cl_limit = self.conf.opticsrad['tel_optics_cl_alt_limit_rad'][1]
        cl_delay = self.conf.optics.tel_optics_cl_delay[1]
        closeLoop = np.where(deltaAlt >= cl_limit)
        slewTime[closeLoop] += cl_delay

        # Mask min/max altitude limits so slewtime = np.nan
        outsideLimits = np.where((alt_rad > self.conf.telrad['altitude_maxpos_rad']) |
                                 (alt_rad < self.conf.telrad['altitude_minpos_rad']))
        slewTime[outsideLimits] = -1
        return slewTime

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
        # Check altitude for target
        if targetposition.alt_rad < self.conf.telrad['altitude_minpos_rad']:
            telalt_rad = self.conf.telrad['altitude_minpos_rad']
            domalt_rad = self.conf.telrad['altitude_minpos_rad']
            valid_state = False

            if "telalt_minpos_rad" in fail_record:
                fail_record["telalt_minpos_rad"] += 1
            else:
                fail_record["telalt_minpos_rad"] = 1

            self.current_state.fail_state = self.current_state.fail_state | \
                                            self.current_state.fail_value_table["altEmin"]

        elif targetposition.alt_rad > self.conf.telrad['altitude_maxpos_rad']:
            telalt_rad = self.conf.telrad['altitude_maxpos_rad']
            domalt_rad = self.conf.telrad['altitude_maxpos_rad']
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

        # Check azimuith for target - including possible cable wrap
        if istracking:
            (telaz_rad, delta) = get_closest_angle_distance(targetposition.az_rad,
                                                                 self.current_state.telaz_rad,
                                                                 wrap_padding=
                                                                 self.conf.telrad['azimuth_wrap_padding_rad'])
            if telaz_rad < self.conf.telrad['azimuth_minpos_rad']:
                telaz_rad = self.conf.telrad['azimuth_minpos_rad']
                valid_state = False
                if "telaz_minpos_rad" in fail_record:
                    fail_record["telaz_minpos_rad"] += 1
                else:
                    fail_record["telaz_minpos_rad"] = 1

                self.current_state.fail_state = self.current_state.fail_state | \
                                                self.current_state.fail_value_table["azEmin"]

            elif telaz_rad > self.conf.telrad['azimuth_maxpos_rad']:
                telaz_rad = self.conf.telrad['azimuth_maxpos_rad']
                valid_state = False
                if "telaz_maxpos_rad" in fail_record:
                    fail_record["telaz_maxpos_rad"] += 1
                else:
                    fail_record["telaz_maxpos_rad"] = 1

                self.current_state.fail_state = self.current_state.fail_state | \
                                                self.current_state.fail_value_table["azEmax"]

        else:
            (telaz_rad, delta) = get_closest_angle_distance(targetposition.az_rad,
                                                                 self.current_state.telaz_rad,
                                                                 self.conf.telrad['azimuth_minpos_rad'],
                                                                 self.conf.telrad['azimuth_maxpos_rad'])

        (domaz_rad, delta) = get_closest_angle_distance(targetposition.az_rad,
                                                             self.current_state.domaz_rad)

        # Check rotator angle
        if istracking:
            (telrot_rad, delta) = get_closest_angle_distance(targetposition.rot_rad,
                                                                  self.current_state.telrot_rad)
            if telrot_rad < self.conf.rotrad['minpos_rad']:
                telrot_rad = self.conf.rotrad['minpos_rad']
                valid_state = False
                if "telrot_minpos_rad" in fail_record:
                    fail_record["telrot_minpos_rad"] += 1
                else:
                    fail_record["telrot_minpos_rad"] = 1

                self.current_state.fail_state = self.current_state.fail_state | \
                                                self.current_state.fail_value_table["rotEmin"]

            elif telrot_rad > self.conf.rotrad['maxpos_rad']:
                telrot_rad = self.conf.rotrad['maxpos_rad']
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
            norm_rot_rad = divmod(targetposition.rot_rad - self.conf.rotrad['minpos_rad'], TWOPI)[1] \
                + self.conf.rotrad['minpos_rad']
            if norm_rot_rad > self.conf.rotrad['maxpos_rad']:
                targetposition.rot_rad = norm_rot_rad - math.pi
            (telrot_rad, delta) = get_closest_angle_distance(targetposition.rot_rad,
                                                                  self.current_state.telrot_rad,
                                                                  self.conf.rotrad['minpos_rad'],
                                                                  self.conf.rotrad['maxpos_rad'])
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
        """Get the observing time for a deep drilling target or sequence of
        exposures which do not slew the telescope.

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
            target.dd_exposures * self.conf.camera.shutter_time + \
            max(target.dd_exposures - 1, 0) * self.conf.camera.readout_time + \
            target.dd_filterchanges * (self.conf.camera.filter_change_time - self.conf.camera.readout_time)

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

        prereq_list = self.prerequisites[activity]

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
        maxspeed = self.conf.domerad['altitude_maxspeed_rad']
        accel = self.conf.domerad['altitude_accel_rad']
        decel = self.conf.domerad['altitude_decel_rad']
        free_range = self.conf.domerad['altitude_freerange_rad']

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
        maxspeed = self.conf.domerad['azimuth_maxspeed_rad']
        accel = self.conf.domerad['azimuth_accel_rad']
        decel = self.conf.domerad['azimuth_decel_rad']
        free_range = self.conf.domerad['azimuth_freerange_rad']

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
            delay = self.conf.dome.settle_time
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
        if targetstate.filterband != initstate.filterband:
            # filter change needed
            delay = self.conf.camera.filter_change_time
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
        return self.conf.camera.readout_time

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
        maxspeed = self.conf.telrad['altitude_maxspeed_rad']
        accel = self.conf.telrad['altitude_accel_rad']
        decel = self.conf.telrad['altitude_decel_rad']

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
        maxspeed = self.conf.telrad['azimuth_maxspeed_rad']
        accel = self.conf.telrad['azimuth_accel_rad']
        decel = self.conf.telrad['azimuth_decel_rad']

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
        for k, cl_delay in enumerate(self.conf.optics.tel_optics_cl_delay):
            if self.conf.opticsrad['tel_optics_cl_alt_limit_rad'][k] <= distance < \
                    self.conf.opticsrad['tel_optics_cl_alt_limit_rad'][k + 1]:
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
            delay = distance * self.conf.opticsrad['tel_optics_ol_slope_rad']
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
        maxspeed = self.conf.rotrad['maxspeed_rad']
        accel = self.conf.rotrad['accel_rad']
        decel = self.conf.rotrad['decel_rad']

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
            delay = self.conf.telescope.settle_time
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
        avg_num = self.conf.camera.filter_max_changes_avg_num
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
        burst_num = self.conf.camera.filter_max_changes_burst_num
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
        """Calculate the slew delay based on the given desired target position.

        Parameters
        ----------
        target : :class:`.ObservatoryPosition`
            An instance of a target position for slew calculation.

        Returns
        -------
        float
            The total slew delay for the target.
        """

        if target.filterband != self.current_state.filterband:
            # check if filter is possible
            if not self.is_filter_change_allowed_for(target.filterband):
                return -1.0, self.current_state.fail_value_table["filter"]

        targetposition = self.radecang2position(self.time,
                                                target.ra_rad,
                                                target.dec_rad,
                                                target.ang_rad,
                                                target.filterband)

        # check if altitude is possible
        if targetposition.alt_rad < self.conf.telrad['altitude_minpos_rad']:
            return -1.0, self.current_state.fail_value_table["altEmin"]
        if targetposition.alt_rad > self.conf.telrad['altitude_maxpos_rad']:
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
        burst_num = self.conf.camera.filter_max_changes_burst_num
        if len(self.filter_changes_list) >= burst_num:
            deltatime = self.current_state.time - self.filter_changes_list[-burst_num]
            if deltatime >= self.conf.camera.filter_max_changes_burst_time:
                # burst time allowed
                avg_num = self.conf.camera.filter_max_changes_avg_num
                if len(self.filter_changes_list) >= avg_num:
                    deltatime = self.current_state.time - self.filter_changes_list[-avg_num]
                    if deltatime >= self.conf.camera.filter_max_changes_avg_time:
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
            target.num_exp * self.conf.camera.shutter_time + \
            max(target.num_exp - 1, 0) * self.conf.camera.readout_time
        self.update_state(self.current_state.time + visit_time)

    def park(self):
        """Put the observatory into the park state.
        """
        self.park_state.filterband = self.current_state.filterband
        slew_delay = self.get_slew_delay_for_state(self.park_state, self.current_state, True)
        self.park_state.time = self.current_state.time + TimeDelta(slew_delay, format='sec')
        self.current_state.set(self.park_state)
        self.update_state(self.park_state.time)

    def reset(self):
            """Reset the observatory state to the parking state - without actually slewing there.
            Does not change current filter or mounted filters.
            """
            self.set_state(self.park_state)

    def set_state(self, new_state):
        """Set observatory state from another state.

        Parameters
        ----------
        new_state : :class:`.ObservatoryState`
            The instance containing the state to update the observatory to.
        """
        if new_state.filterband != self.current_state.filterband:
            self.filter_changes_list.append(new_state.time)

        self.current_state.set(new_state)
        self.time = new_state.time

    def slew(self, target):
        """Slew the observatory to the given target location.

        Parameters
        ----------
        target : :class:`.Target`
            The instance containing the target information for the slew.
        """
        self.slew_radec(self.current_state.time,
                        target.ra_rad, target.dec_rad, target.ang_rad, target.filterband)

    def slew_altaz(self, time, alt_rad, az_rad, rot_rad, filterband):
        """Slew observatory to the given alt, az location.

        Parameters
        ----------
        time : float
            The astropy.time.Time of the request.
        alt_rad : float
            The altitude (radians) to slew to.
        az_rad : float
            The azimuth (radians) to slew to.
        rot_rad : float
            The telescope rotator angle (radians) for the slew.
        filterband : str
            The band filter for the slew.
        """
        self.update_state(time)
        time = self.current_state.time

        targetposition = ObservatoryPosition(time=time, alt_rad=alt_rad, az_rad=az_rad,
                                             rot_rad=rot_rad, filterband=filterband,
                                             tracking=False)
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
        filterband : str
            The band filter for the slew.
        """
        self.update_state(time)
        time = self.current_state.time
        # Note that the targetposition generated from radecang2position has Track=True
        targetposition = self.radecang2position(time, ra_rad, dec_rad, ang_rad, filter)

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
        if targetposition.filterband != self.current_state.filterband:
            self.filter_changes_list.append(targetstate.time)
        targetstate.time = targetstate.time + TimeDelta(slew_delay, format='sec')
        self.current_state.set(targetstate)
        self.update_state(targetstate.time)

    def start_tracking(self, time):
        """Put observatory into tracking mode.

        Parameters
        ----------
        time : astropy.time.Time
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
        time : astropy.time.Time
        """
        if time < self.current_state.time:
            time = self.current_state.time
        if self.current_state.tracking:
            self.update_state(time)
            self.current_state.tracking = False

    def unmount_filter(self, filter_to_unmount):
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
            self.log.info("mount_filter: REJECTED filter %s is not mounted" %
                          (filter_to_unmount))

    def update_state(self, time=None):
        """Update the observatory state for the given time.

        If the specified time is < the current state time, uses the current state instead.
        Updates ra/dec for current alt/az (if not tracking) or
        updates alt/az for current (ra/dec) if tracking.

        Parameters
        ----------
        time : astropy.time.Time (opt)
            Time to use to sync up ra/dec - alt/az values.
            If None, then uses current_state.time
        """
        if time is None:
            time = self.current_state.time
        if time < self.current_state.time:
            time = self.current_state.time
        self.time = time

        if self.current_state.tracking:

            target = Target
            obsposition = self.radecang2position(time,
                                                    self.current_state.ra_rad,
                                                    self.current_state.dec_rad,
                                                    self.current_state.ang_rad,
                                                    self.current_state.filterband)

            targetstate = self.get_closest_state(obsposition, istracking=True)

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
            (ra_rad, dec_rad, pa_rad) = self.altaz2radecpa(self.calcLst(time),
                                                           self.current_state.alt_rad,
                                                           self.current_state.az_rad)
            self.current_state.time = time
            self.current_state.ra_rad = ra_rad
            self.current_state.dec_rad = dec_rad
            self.current_state.ang_rad = divmod(pa_rad - self.current_state.rot_rad, TWOPI)[1]
            self.current_state.pa_rad = pa_rad