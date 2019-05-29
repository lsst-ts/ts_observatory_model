import math
import json


__all__ = ["Target"]


class Target(object):
    """Target defines a desired pointing for the telescope.

    Target is converted to a full ObservatoryPosition (which specifies the complete details of the pointing)
    when a specific TIME is added to the calculation.
    That is, at a given time, ra/dec implies a particular alt/az (or vice versa) and these will be calculated
    by the ObservatoryPosition.
    In addition, at any given time, the parallactic angle (angle between North and the zenith) for the
    ra/dec/alt/az values is fixed. Since
    rotator angle (rotTelPos) = (parallactic angle - sky angle (rotSkyPos)) % 2PI


    While there are defaults available, there is a minimum requirement of setting
    a pair of either RA/Dec or alt/az values (ra_rad/dec_rad or alt_rad/az_rad).
    If ra/dec is specified, alt/az will be ignored.

    Parameters
    ----------
    targetid : int, opt
        A unique identifier for the given target. Default 0.
        This simply aids in identification, but is not important to the ObservatoryModel.
    filterband : str, opt
        The single character name of the associated band filter.
        Default None - in which case, the current filter in use will be filled by the ObservatoryModel.
    ra_rad : float, opt
        The right ascension (radians) of the target. Default None.
        If ra_rad is specified, input is expected to be ra/dec and the alt/az values will be ignored.
    dec_rad : float, opt
        The declination (radians) of the target. Default None.
    ang_rad : float, opt
        The sky angle (radians) of the target [angle between y and N]. Default None.
        If ang_rad is specified, rot_rad will be ignored.
    alt_rad : float, opt
        The altitude (radians) of the target. Default None.
        If alt_rad is specified (and not ra_rad), the input is expected to be alt/az.
    az_rad : float, opt
        The azimuth (radians) of of the target. Default None.
    rot_rad : float, opt
        The rotator angle (radians) of the camera [angle between y and zenith]. Default None.
        If ang_rad is specified, this value is ignored.
        If both values are None, the rotator angle will be set to 0.
    num_exp : int, opt
        The number of requested exposures for the target. Default 2.
    exp_times : list[float], opt
        The set of exposure times (seconds) for the target. Default [15, 15].
        Length needs to match num_exp.
    """

    def __init__(self, targetid=0, filterband=None,
                 ra_rad=None, dec_rad=None, ang_rad=None,
                 alt_rad=None, az_rad=None, rot_rad=None,
                 num_exp=2, exp_times=[15, 15]):

        self.targetid = targetid
        self.filterband = filterband

        # Use ra/dec if available and ignore alt/az.
        if ra_rad is not None:
            if dec_rad is None:
                raise ValueError('Must define both RA/Dec values.')
            self.ra_rad = ra_rad
            self.dec_rad = dec_rad
            self.alt_rad = None
            self.az_rad = None
        elif alt_rad is not None:
            if az_rad is None:
                raise ValueError('Must define both alt/az values.')
            self.ra_rad = None
            self.dec_rad = None
            self.alt_rad = alt_rad
            self.az_rad = az_rad
        else:
            raise ValueError('Must define either ra/dec or alt/az values.')

        # Check if ang (rotSkyPos) or rotator (rotTelPos) positions specified.
        if ang_rad is not None:
            self.ang_rad = ang_rad
            self.rot_rad = None
        elif rot_rad is not None:
            self.rot_rad = rot_rad
            self.ang_rad = None
        else:
            self.ang_rad = None
            self.rot_rad = 0.0

        self.num_exp = num_exp
        self.exp_times = list(exp_times)
        # Check that length of exp_times matches num_exp.
        if len(self.exp_times) != self.num_exp:
            raise ValueError('Length of exp_times (%d) must match num_exp (%d).'
                             % (len(self.exp_times), self.num_exp))
        self._exp_time = sum(self.exp_times)  # total on-sky exposure time

    def __str__(self):
        """str: The string representation of the instance."""
        s = f'targetid {self.targetid} filterband {self.filterband} numexp {self.num_exp} exp_times {self.exp_times}'
        s += f' ra {self.ra} dec {self.dec} ang {self.ang} alt {self.alt} az {self.az} rot {self.rot}'
        return s

    @property
    def alt(self):
        """float: The altitude (degrees) of the target."""
        try:
            return math.degrees(self.alt_rad)
        except TypeError:
            return None

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
        try:
            return math.degrees(self.ang_rad)
        except TypeError:
            return None

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
        try:
            return math.degrees(self.az_rad)
        except TypeError:
            return None

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
        try:
            return math.degrees(self.dec_rad)
        except TypeError:
            return None

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
        try:
            return math.degrees(self.ra_rad)
        except TypeError:
            return None

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
        try:
            return math.degrees(self.rot_rad)
        except TypeError:
            return None

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
    def total_exp_time(self):
        """

        Returns
        -------
        exp_time: float: The total on-sky exposure time in seconds.
        """
        return self._exp_time

    def to_json(self):
        """
        Returns a json serialization of variables in this object
        """
        return json.dumps(vars(self))

    def from_json(self, jsonstr):
        """
        alternate __init__ method that takes a json representation as the only argument
        (this likely needs an update, to enable specification of a target via alt/az and rot OR ang)
        """
        mandatory_fields = ["targetid", "filterband", "ra_rad", "dec_rad",
                            "ang_rad", "num_exp", "exp_times"]

        jsondict = json.loads(jsonstr)
        for f in mandatory_fields:
            if f not in jsondict.keys():
                raise KeyError("json blob passed to Target()'s json constructor "
                               "is missing required attribute: " + f)

        for k in jsondict:
            setattr(self, k, jsondict[k])

    @classmethod
    def from_topic(cls, topic):
        """Alternate initializer.
        (This likely needs an update, to enable specification of a target via alt/az and rot OR skyAngle).

        Parameters
        ----------
        topic : SALPY_scheduler.targetC
            The target topic instance.

        Returns
        -------
        :class:`.Target`
        """
        return cls(topic.targetId, topic.filter,
                   math.radians(topic.ra), math.radians(topic.decl), math.radians(topic.skyAngle),
                   None, None, None,
                   topic.numExposures, topic.exposureTimes)
