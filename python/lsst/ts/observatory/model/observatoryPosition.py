import math
from .utils import SiteUtils
from .target import Target

__all__ = ["ObservatoryPosition"]


class ObservatoryPosition(object):
    """Class for providing base pointing position information.
    This is a fully defined position at a particular TIME.

    Note that "time" and "tracking" are key parameters.
    If "tracking" is True, then RA/Dec/ang will remain up-to-date, while
    the alt/az/rot values will change over time.
    If "tracking" is False, then alt/az/rot values will remain up-to-date,
    while the RA/Dec/ang values will change over time.
    (PA - the parallactic angle) will always change over time.

    Parameters
    ----------
    time : astropy.time.Time, opt
        The time for the given pointing information.
    ra_rad : float, opt
        The right ascension (radians) for the pointing position.
    dec_rad : float, opt
        The declination (radians) for the pointing position.
    ang_rad : float, opt
        The position angle (radians) for the pointing position (angle between y & N). [rotSkyPos].
    filterband : str, opt
        The band filter being used during the pointing.
    tracking : bool, opt
        The tracking state of the pointing.
    alt_rad : float, opt
        The altitude (radians) of the pointing.
    az_rad : float, opt
        The azimuth (radians) of the pointing.
    pa_rad : float, opt
        The parallactic angle (radians) of the pointing.
    rot_rad : float, opt
        The camera rotator angle (radians) of the pointing (between y & zenith). [rotTelPos].
    site : lsst.ts.observatory.model.SiteUtils, opt
    """

    def __init__(self, time=None, ra_rad=0.0, dec_rad=0.0, ang_rad=0.0,
                 filterband='r', tracking=False, alt_rad=1.5, az_rad=0.0,
                 pa_rad=0.0, rot_rad=0.0, site=None):
        """Initialize the class.
        """
        self.time = time
        self.ra_rad = ra_rad
        self.dec_rad = dec_rad
        self.ang_rad = ang_rad
        self.filterband = filterband
        self.tracking = tracking
        self.alt_rad = alt_rad
        self.az_rad = az_rad
        self.pa_rad = pa_rad
        self.rot_rad = rot_rad
        if site is None:
            self.site = SiteUtils()
        else:
            self.site = site

    def __str__(self):
        """str: The string representation of the instance."""
        return "t=%f ra=%.3f dec=%.3f ang=%.3f filter=%s track=%s alt=%.3f "\
               "az=%.3f pa=%.3f rot=%.3f" % \
               (self.time.tai.mjd, self.ra, self.dec, self.ang, self.filterband,
                self.tracking, self.alt, self.az, self.pa, self.rot)

    def setPositionFromTarget(self, target, time):
        """Using the parameters in Target, calculate a full ObservatoryPosition.

        Parameters
        ----------
        target : lsst.ts.observatory.Target
            The desired target pointing
        time : astropy.time.Time
            The time to implement the target pointing at (i.e. specifies alt/az from ra/dec,
            or vice versa, and rotator angle from skyAng or vice versa.)
        """



    def radecang2position(self, time, ra_rad, dec_rad, ang_rad, filterband):
        """Convert current time, sky location and filter into observatory\
           position.

        Parameters
        ----------
        time : astropy.time.Time
            The current time.
        ra_rad : float
            The current right ascension (radians).
        dec_rad : float
            The current declination (radians).
        ang_rad : float
            The current sky angle (radians).
        filterband : str
            The current band filter.

        Returns
        -------
        :class:`.ObservatoryPosition`
            The observatory position information from inputs.
        """
        (alt_rad, az_rad, pa_rad) = self.radec2altazpa(self.calcLst(time), ra_rad, dec_rad)

        position = ObservatoryPosition(time=time, tracking=True,
                                       ra_rad=ra_rad, dec_rad=dec_rad, ang_rad=ang_rad,
                                       filterband=filterband,
                                       alt_rad=alt_rad, az_rad=az_rad, pa_rad=pa_rad,
                                       rot_rad=divmod(pa_rad - ang_rad, TWOPI)[1])
        return position

    @property
    def alt(self):
        """float: Return the altitude (degrees) of the pointing position."""
        return math.degrees(self.alt_rad)

    @property
    def ang(self):
        return math.degrees(self.ang_rad)

    @property
    def az(self):
        """float: Return the azimuth (degrees) of the pointing position."""
        return math.degrees(self.az_rad)

    @property
    def dec(self):
        """float: Return the declination (degrees) of the pointing
                  position."""
        return math.degrees(self.dec_rad)

    @property
    def pa(self):
        """float: Return the parallactic angle (degrees) of the pointing
                  position."""
        return math.degrees(self.pa_rad)

    @property
    def ra(self):
        """float: Return the right ascension (degrees) of the pointing
                  position."""
        return math.degrees(self.ra_rad)

    @property
    def rot(self):
        return math.degrees(self.rot_rad)
