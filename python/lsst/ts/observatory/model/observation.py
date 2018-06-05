import math
import numpy

__all__ = ["Observation"]

class Observation(object):
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
        
        #Observation fields
        self.observationid = 0
        self.observation_start_time = 0
        self.observation_start_mjd = 0 
        self.observation_start_lst = 0
        self.night = 0
        self.targetid = targetid = 0
        self.fieldid = fieldid = 0
        self.groupid = 0
        self.filter = band_filter
        self.num_props = 0
        self.propid_list = []
        self.ra_rad = ra_rad
        self.dec_rad = dec_rad
        self.ang_rad = ang_rad
        self.alt_rad = 0.0
        self.az_rad = 0.0    
        self.num_exp = num_exp
        self.exp_times = list(exp_times)
        self.visit_time = 0
        self.sky_brightness = 0.0
        self.airmass = 0.0
        self.cloud = 0.0
        self.seeing_fwhm_500 = 0
        self.seeing_fwhm_geom = 0
        self.seeing_fwhm_eff = 0
        self.five_sigma_depth = 0
        self.moon_ra = 0
        self.moon_dec = 0
        self.moon_alt = 0
        self.moon_az = 0
        self.moon_phase = 0
        self.moon_distance = 0
        self.sun_alt = 0
        self.sun_az = 0
        self.sun_ra = 0
        self.sun_dec = 0
        self.solar_elong = 0
        self.slewTime = 0


        #previously, we'd been using the Target class as a standin for Observation
        #in scheduler. Below are the variables present in Target but not Observation,
        #to preserve compatibility. At some point this should be tidied up. 
        
        # conditions
        self.time = 0.0
        self.seeing = 0.0

        # computed at proposal
        self.propid = 0
        self.need = 0.0
        self.bonus = 0.0
        self.value = 0.0
        # internal proposal book-keeping
        self.goal = 0
        self.visits = 0
        self.progress = 0.0

        self.sequenceid = 0
        self.subsequencename = ""
        self.groupid = 0
        self.groupix = 0
        self.is_deep_drilling = False
        self.is_dd_firstvisit = False
        self.remaining_dd_visits = 0
        self.dd_exposures = 0
        self.dd_filterchanges = 0
        self.dd_exptime = 0.0

        # computed at driver
        
        self.rot_rad = 0.0
        self.telalt_rad = 0.0
        self.telaz_rad = 0.0
        self.telrot_rad = 0.0
        self.propboost = 1.0
        self.slewtime = 0.0
        self.cost = 0.0
        self.rank = 0.0

        # assembled at driver
        
        
        self.need_list = []
        self.bonus_list = []
        self.value_list = []
        self.propboost_list = []
        self.sequenceid_list = []
        self.subsequencename_list = []
        self.groupid_list = []
        self.groupix_list = []
        self.is_deep_drilling_list = []
        self.is_dd_firstvisit_list = []
        self.remaining_dd_visits_list = []
        self.dd_exposures_list = []
        self.dd_filterchanges_list = []
        self.dd_exptime_list = []

        # stamped at observation
        self.last_visit_time = 0.0

        #additional variables present in Observation SAL topic
     

    def __str__(self):
        """str: The string representation of the instance."""
        return ("targetid=%d field=%d filter=%s exp_times=%s ra=%.3f "
                "dec=%.3f ang=%.3f alt=%.3f az=%.3f "
                "observationid=%d "
                "time=%.1f airmass=%.3f brightness=%.3f "
                "cloud=%.2f seeing=%.2f "
                "visits=%i progress=%.2f%% "
                "seqid=%i ssname=%s groupid=%i groupix=%i "
                "propid=%s "
                "slewTime=%.3f" %
                (self.targetid, self.fieldid, self.filter,
                 str(self.exp_times),
                 self.ra, self.dec, self.ang,
                 self.alt, self.az,
                 self.observationid,
                 self.time, self.airmass, self.sky_brightness,
                 self.cloud, self.seeing,
                 self.visits, 100 * self.progress,
                 self.sequenceid, self.subsequencename,
                 self.groupid, self.groupix,
                 self.propid_list,
                 self.slewTime))

    @property
    def alt(self):
        """float: The altitude (degrees) of the target."""
        return math.degrees(self.alt_rad)

    @property
    def ang(self):
        """float: The sky angle (degrees) of the target."""
        return math.degrees(self.ang_rad)

    @property
    def az(self):
        """float: The azimuth (degrees) of the target."""
        return math.degrees(self.az_rad)

    @property
    def dec(self):
        """float: The declination (degrees) of the target."""
        return math.degrees(self.dec_rad)

    @property
    def ra(self):
        """float: The right ascension (degrees) of the target."""
        return math.degrees(self.ra_rad)

    @property
    def rot(self):
        """float: The rotator angle (degrees) of the target."""
        return math.degrees(self.rot_rad)

    @property
    def telalt(self):
        """float: The telescope altitude (degrees) for the target."""
        return math.degrees(self.telalt_rad)

    @property
    def telaz(self):
        """float: The telescope azimuth (degrees) for the target."""
        return math.degrees(self.telaz_rad)

    @property
    def telrot(self):
        """float: The telescope rotator angle (degrees) for the target."""
        return math.degrees(self.telrot_rad)

    def copy_driver_state(self, target):
        """Copy driver state from another target.

        Parameters
        ----------
        target : :class:`.Target`
            An instance of a target from which to get the driver state
            information.
        """
        self.alt_rad = target.alt_rad
        self.az_rad = target.az_rad
        self.rot_rad = target.rot_rad
        self.telalt_rad = target.telalt_rad
        self.telaz_rad = target.telaz_rad
        self.telrot_rad = target.telrot_rad
        self.ang_rad = target.ang_rad

    def get_copy(self):
        """:class:`.Observation`: Get copy of the instance."""
        newobservation = Observation()
        newobservation.observationid = self.observationid
        newobservation.observation_start_time = self.observation_start_time
        newobservation.observation_start_mjd = self.observation_start_mjd 
        newobservation.observation_start_lst = self.observation_start_lst
        newobservation.night = self.night
        newobservation.targetid = self.targetid
        newobservation.fieldid = self.fieldid
        newobservation.groupid = self.groupid
        newobservation.filter = self.filter
        newobservation.num_props = self.num_props
        newobservation.propid_list = self.propid_list
        newobservation.ra_rad = self.ra_rad
        newobservation.dec_rad = self.dec_rad
        newobservation.ang_rad = self.ang_rad
        newobservation.alt_rad = self.alt_rad
        newobservation.az_rad = self.az_rad
        newobservation.num_exp = self.num_exp 
        newobservation.exp_times = self.exp_times
        newobservation.visit_time = self.visit_time
        newobservation.sky_brightness = self.sky_brightness
        newobservation.airmass = self.airmass
        newobservation.cloud = self.cloud
        newobservation.seeing_fwhm_500 = self.seeing_fwhm_500
        newobservation.seeing_fwhm_geom = self.seeing_fwhm_geom
        newobservation.seeing_fwhm_eff = self.seeing_fwhm_eff
        newobservation.five_sigma_depth = self.five_sigma_depth
        newobservation.moon_ra = self.moon_ra
        newobservation.moon_dec = self.moon_dec
        newobservation.moon_alt = self.moon_alt
        newobservation.moon_az = self.moon_az
        newobservation.moon_phase = self.moon_phase
        newobservation.moon_distance = self.moon_distance
        newobservation.sun_alt = self.sun_alt
        newobservation.sun_az = self.sun_az
        newobservation.sun_ra = self.sun_ra
        newobservation.sun_dec = self.sun_dec
        newobservation.solar_elong = self.solar_elong
        newobservation.slewTime = self.slewTime

        
        #everything below this is legacy fields from Target, that don't belong in Observation. 
        #we should get rid of these if leaving them out doesn't break anything...
        weNeedThis = False
        if weNeedThis:
            newobservation.rot_rad = self.rot_rad
            newobservation.telalt_rad = self.telalt_rad
            newobservation.telaz_rad = self.telaz_rad
            newobservation.telrot_rad = self.telrot_rad
            newobservation.propboost = self.propboost
            newobservation.slewtime = self.slewtime
            newobservation.cost = self.cost
            newobservation.rank = self.rank
            newobservation.num_props = self.num_props
            newobservation.propid_list = list(self.propid_list)
            newobservation.need_list = list(self.need_list)
            newobservation.bonus_list = list(self.bonus_list)
            newobservation.value_list = list(self.value_list)
            newobservation.propboost_list = list(self.propboost_list)
            newobservation.sequenceid_list = list(self.sequenceid_list)
            newobservation.subsequencename_list = list(self.subsequencename_list)
            newobservation.groupid_list = list(self.groupid_list)
            newobservation.groupix_list = list(self.groupix_list)
            newobservation.is_deep_drilling_list = list(self.is_deep_drilling_list)
            newobservation.is_dd_firstvisit_list = list(self.is_dd_firstvisit_list)
            newobservation.remaining_dd_visits_list = list(self.remaining_dd_visits_list)
            newobservation.dd_exposures_list = list(self.dd_exposures_list)
            newobservation.dd_filterchanges_list = list(self.dd_filterchanges_list)
            newobservation.dd_exptime_list = list(self.dd_exptime_list)

            #legacy stuff
            newobservation.time = self.time
            newobservation.seeing = self.seeing
            newobservation.propid = self.propid
            newobservation.need = self.need
            newobservation.bonus = self.bonus
            newobservation.value = self.value
            newobservation.goal = self.goal
            newobservation.visits = self.visits
            newobservation.progress = self.progress

            newobservation.sequenceid = self.sequenceid
            newobservation.subsequencename = self.subsequencename
            newobservation.groupix = self.groupix
            newobservation.is_deep_drilling = self.is_deep_drilling
            newobservation.is_dd_firstvisit = self.is_dd_firstvisit
            newobservation.remaining_dd_visits = self.remaining_dd_visits
            newobservation.dd_exposures = self.dd_exposures
            newobservation.dd_filterchanges = self.dd_filterchanges
            newobservation.dd_exptime = self.dd_exptime

        return newobservation

    @classmethod
    def from_topic(cls, topic):
        """Alternate initializer.

        Parameters
        ----------
        topic : SALPY_scheduler.targetC
            The target topic instance.

        Returns
        -------
        :class:`.Target`
        """
        return cls(topic.targetId, topic.fieldId, topic.filter, math.radians(topic.ra),
                   math.radians(topic.decl), math.radians(topic.angle), topic.num_exposures,
                   topic.exposure_times)
