import math
import numpy
import copy
import json

__all__ = ["Target"]

class Target(object):
    """Class for gathering information for a sky target.
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
        self.targetid = targetid
        self.fieldid = fieldid
        self.filter = band_filter
        self.ra_rad = ra_rad
        self.dec_rad = dec_rad
        self.ang_rad = ang_rad
        self.num_exp = num_exp
        self.exp_times = list(exp_times)
        self._exp_time = None  # total exposure time

        # conditions
        self.time = 0.0
        self.airmass = 0.0
        self.sky_brightness = 0.0
        self.cloud = 0.0
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
        self.alt_rad = 0.0
        self.az_rad = 0.0
        self.rot_rad = 0.0
        self.telalt_rad = 0.0
        self.telaz_rad = 0.0
        self.telrot_rad = 0.0
        self.propboost = 1.0
        self.slewtime = 0.0
        self.cost = 0.0
        self.rank = 0.0

        # assembled at driver
        self.num_props = 0
        self.propid_list = []
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

        self.note = ''

    def __str__(self):
        """str: The string representation of the instance."""
        return ("targetid=%d field=%d filter=%s exp_times=%s ra=%.3f "
                "dec=%.3f ang=%.3f alt=%.3f az=%.3f rot=%.3f "
                "telalt=%.3f telaz=%.3f telrot=%.3f "
                "time=%.1f airmass=%.3f brightness=%.3f "
                "cloud=%.2f seeing=%.2f "
                "visits=%i progress=%.2f%% "
                "seqid=%i ssname=%s groupid=%i groupix=%i "
                "firstdd=%s ddvisits=%i "
                "need=%.3f bonus=%.3f value=%.3f propboost=%.3f "
                "propid=%s need=%s bonus=%s value=%s propboost=%s "
                "slewtime=%.3f cost=%.3f rank=%.3f note=%s" %
                (self.targetid, self.fieldid, self.filter,
                 str(self.exp_times),
                 self.ra, self.dec, self.ang,
                 self.alt, self.az, self.rot,
                 self.telalt, self.telaz, self.telrot,
                 self.time, self.airmass, self.sky_brightness,
                 self.cloud, self.seeing,
                 self.visits, 100 * self.progress,
                 self.sequenceid, self.subsequencename,
                 self.groupid, self.groupix,
                 self.is_dd_firstvisit, self.remaining_dd_visits,
                 self.need, self.bonus, self.value, self.propboost,
                 self.propid_list, numpy.round(self.need_list, 3), numpy.round(self.bonus_list, 3),
                 numpy.round(self.value_list, 3), numpy.round(self.propboost_list, 3),
                 self.slewtime, self.cost, self.rank, self.note))

    @property
    def alt(self):
        """float: The altitude (degrees) of the target."""
        return math.degrees(self.alt_rad)

    @alt.setter
    def alt(self, alt):
        """
        Set altitude given in degrees

        Parameters
        ----------
         alt: float (degrees)
        """
        self.alt_rad = math.radians(alt)

    @property
    def ang(self):
        """float: The sky angle (degrees) of the target."""
        return math.degrees(self.ang_rad)

    @ang.setter
    def ang(self, ang):
        """
        Set camera rotation angle given in degrees

        Parameters
        ----------
         ang: float (degrees)
        """
        self.ang_rad = math.radians(ang)

    @property
    def az(self):
        """float: The azimuth (degrees) of the target."""
        return math.degrees(self.az_rad)

    @az.setter
    def az(self, az):
        """
        Set camera rotation angle given in degrees

        Parameters
        ----------
         az: float (degrees)
        """
        self.az_rad = math.radians(az)

    @property
    def dec(self):
        """float: The declination (degrees) of the target."""
        return math.degrees(self.dec_rad)

    @dec.setter
    def dec(self, dec):
        """
        Set declination given in degrees

        Parameters
        ----------
         dec: float (degrees)
        """
        self.dec_rad = math.radians(dec)

    @property
    def ra(self):
        """float: The right ascension (degrees) of the target."""
        return math.degrees(self.ra_rad)

    @ra.setter
    def ra(self, ra):
        """
        Set right ascension given in degrees

        Parameters
        ----------
         ra: float (degrees)
        """
        self.ra_rad = math.radians(ra)

    @property
    def rot(self):
        """float: The rotator angle (degrees) of the target."""
        return math.degrees(self.rot_rad)

    @rot.setter
    def rot(self, rot):
        """
        Set camera rotation angle given in degrees

        Parameters
        ----------
         rot: float (degrees)
        """
        self.rot_rad = math.radians(rot)

    @property
    def telalt(self):
        """float: The telescope altitude (degrees) for the target."""
        return math.degrees(self.telalt_rad)

    @telalt.setter
    def telalt(self, telalt):
        """
        Set camera rotation angle given in degrees

        Parameters
        ----------
         telalt: float (degrees)
        """
        self.telalt_rad = math.radians(telalt)

    @property
    def telaz(self):
        """float: The telescope azimuth (degrees) for the target."""
        return math.degrees(self.telaz_rad)

    @telaz.setter
    def telaz(self, telaz):
        """
        Set camera rotation angle given in degrees

        Parameters
        ----------
         telaz: float (degrees)
        """
        self.telaz_rad = math.radians(telaz)

    @property
    def telrot(self):
        """float: The telescope rotator angle (degrees) for the target."""
        return math.degrees(self.telrot_rad)

    @telrot.setter
    def telrot(self, telrot):
        """
        Set camera rotation angle given in degrees

        Parameters
        ----------
         telrot: float (degrees)
        """
        self.telrot_rad = math.radians(telrot)

    @property
    def exp_time(self):
        """

        Returns
        -------
        exp_time: float: The total exposure time in seconds.
        """
        if self._exp_time is None:
            return sum(self.exp_times)
        else:
            self._exp_time

    @exp_time.setter
    def exp_time(self, exp_time):
        """

        Parameters
        ----------
        exp_time: float: The total exposure time in seconds.

        Returns
        -------
        None
        """
        self._exp_time = exp_time

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
        """:class:`.Target`: Get copy of the instance."""
        newtarget = Target()
        newtarget.targetid = self.targetid
        newtarget.fieldid = self.fieldid
        newtarget.filter = self.filter
        newtarget.ra_rad = self.ra_rad
        newtarget.dec_rad = self.dec_rad
        newtarget.ang_rad = self.ang_rad
        newtarget.num_exp = self.num_exp
        newtarget.exp_times = list(self.exp_times)
        newtarget.time = self.time
        newtarget.airmass = self.airmass
        newtarget.sky_brightness = self.sky_brightness
        newtarget.cloud = self.cloud
        newtarget.seeing = self.seeing
        newtarget.propid = self.propid
        newtarget.need = self.need
        newtarget.bonus = self.bonus
        newtarget.value = self.value
        newtarget.goal = self.goal
        newtarget.visits = self.visits
        newtarget.progress = self.progress

        newtarget.sequenceid = self.sequenceid
        newtarget.subsequencename = self.subsequencename
        newtarget.groupid = self.groupid
        newtarget.groupix = self.groupix
        newtarget.is_deep_drilling = self.is_deep_drilling
        newtarget.is_dd_firstvisit = self.is_dd_firstvisit
        newtarget.remaining_dd_visits = self.remaining_dd_visits
        newtarget.dd_exposures = self.dd_exposures
        newtarget.dd_filterchanges = self.dd_filterchanges
        newtarget.dd_exptime = self.dd_exptime

        newtarget.alt_rad = self.alt_rad
        newtarget.az_rad = self.az_rad
        newtarget.rot_rad = self.rot_rad
        newtarget.telalt_rad = self.telalt_rad
        newtarget.telaz_rad = self.telaz_rad
        newtarget.telrot_rad = self.telrot_rad
        newtarget.propboost = self.propboost
        newtarget.slewtime = self.slewtime
        newtarget.cost = self.cost
        newtarget.rank = self.rank
        newtarget.num_props = self.num_props
        newtarget.propid_list = list(self.propid_list)
        newtarget.need_list = list(self.need_list)
        newtarget.bonus_list = list(self.bonus_list)
        newtarget.value_list = list(self.value_list)
        newtarget.propboost_list = list(self.propboost_list)
        newtarget.sequenceid_list = list(self.sequenceid_list)
        newtarget.subsequencename_list = list(self.subsequencename_list)
        newtarget.groupid_list = list(self.groupid_list)
        newtarget.groupix_list = list(self.groupix_list)
        newtarget.is_deep_drilling_list = list(self.is_deep_drilling_list)
        newtarget.is_dd_firstvisit_list = list(self.is_dd_firstvisit_list)
        newtarget.remaining_dd_visits_list = list(self.remaining_dd_visits_list)
        newtarget.dd_exposures_list = list(self.dd_exposures_list)
        newtarget.dd_filterchanges_list = list(self.dd_filterchanges_list)
        newtarget.dd_exptime_list = list(self.dd_exptime_list)

        newtarget.note = self.note

        return newtarget

    def to_json(self):
        """
        Returns a json serialization of variables in this object
        """
        return json.dumps(vars(self))

    def from_json(self, jsonstr):
        """
        alternate __init__ method that takes a json representation as the only argument
        """
        mandatory_fields = ["targetid", "fieldid", "filter", "ra_rad", "dec_rad", "ang_rad", "num_exp", "exp_times"]

        jsondict = json.loads(jsonstr)
        for f in mandatory_fields:
            if f not in jsondict.keys():
                raise KeyError("json blob passed to Target()'s json constructor is missing required attribute: " + f)


        for k in jsondict:
            setattr(self, k, jsondict[k])   

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
        return cls(topic.targetId, -1, topic.filter, math.radians(topic.ra),
                   math.radians(topic.decl), math.radians(topic.skyAngle), topic.numExposures,
                   topic.exposureTimes)
