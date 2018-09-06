import math
from lsst.ts.observatory.model import Target
import logging

__all__ = ["Observation"]

logger = logging.getLogger(__name__)

class Observation(Target):
    """
    """

    def __init__(self, targetid=0, fieldid=0, band_filter="",
                 ra_rad=0.0, dec_rad=0.0, ang_rad=0.0,
                 num_exp=0, exp_times=[]):
        """Initialize the class.

        Parameters
        ----------
        targetid : int
            A unique identifier for the given target.
        fieldid : int
            The ID of the associated OpSim field for the target.
        band_filter : str
            The single character name of the associated band filter.
        ra_rad : float
            The right ascension (radians) of the target.
        dec_rad : float
            The declination (radians) of the target.
        ang_rad : float
            The sky angle (radians) of the target.
        num_exp : int
            The number of requested exposures for the target.
        exp_times : list[float]
            The set of exposure times for the target. Needs to length
            of num_exp.
        """
        
        super(Observation, self).__init__(targetid=targetid, fieldid=fieldid, band_filter=band_filter,
                                          ra_rad=ra_rad, dec_rad=dec_rad, ang_rad=ang_rad, num_exp=num_exp,
                                          exp_times=exp_times)

        self.altitude = 0.
        self.azimuth = 0.
        self.angle = 0.
        self.fieldId = 0
        self.five_sigma_depth = 0.
        self.groupId = 0
        self.night = 0
        self.observation_id = 0
        self.observation_start_lst = 0.
        self.observation_start_mjd = 0.
        self.observation_start_time = 0.
        self.seeing_fwhm_500 = 0.
        self.seeing_fwhm_eff = 0.
        self.seeing_fwhm_geom = 0.
        self.visit_time = 0.
        self.moon_alt = 0.
        self.sun_alt = 0.

    @classmethod
    def from_topic(cls, topic):
        """Alternate initializer.

        Parameters
        ----------
        topic : SALPY_scheduler.scheduler_observationC
            The target topic instance.

        Returns
        -------
        :class:`.Target`
        """
        return cls(topic.targetId, topic.fieldId, topic.filter, math.radians(topic.ra),
                   math.radians(topic.decl), math.radians(topic.angle), topic.num_exposures,
                   topic.exposure_times)

    @staticmethod
    def make_copy(observation, check=False):
        """
        Receives an iterable object (like a dictionary) and return a copy of Observation. If check==True makes sure
        the basic parameters are part of observation. Raise an exception otherwise.

        :param observation:
        :param check:
        :return:
        """
        ret_obs = Observation()

        for key in observation:
            try:
                setattr(ret_obs, key, observation[key])
            except AttributeError as e:
                logger.error('Cannot set %s: %s', key, observation[key])


        return ret_obs
