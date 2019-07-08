import math
from .utils import SiteUtils

__all__ = ["ObservatoryPosition"]


class ObservatoryPosition(object):
    """Class for providing base pointing position information.
    This is a fully defined position at a particular TIME from a particular SITE.
    (i.e. a target + time + site == position).

    Note that "time" and "site" are key parameters.
    "site" is used to calculate alt/az from ra/dec.
    (PA - the parallactic angle) will always change over time, but either ra/dec OR alt/az will be constant.
    pa_rad = parallactic angle (radians) of the target [angle between lines to zenith and north]
    ang_rad = The sky angle (radians) of the target [angle between y and N]. (rotSkyPos)
    rot_rad = The angle (radians) of the target [angle between y and zenith/up]. (rotTelPos)
    ang_rad = (pa_rad - rot_rad) % 2pi

    Parameters
    ----------
    time : astropy.time.Time
        The time for the given pointing information.
    target : lsst.ts.observatory.model.Target
        The desired pointing location. Note that either ra/dec or alt/az need to be specified, together
        with either rotSkyPos or rotTelPos.
    site : lsst.ts.observatory.model.SiteUtils, opt
        Location of site (lsst.sims.utils.Site) plus additional utilities to calculate LST and convert
        between alt/az and ra/dec. Default is LSST site.
    """

    def __init__(self, time, target, site=None):
        # Note that observatoryposition.tracking was removed in this update, as it seemed to be
        # unused anywhere.
        if site is None:
            self.site = SiteUtils()
        else:
            self.site = site
        self.time = time
        self.time = time
        self.filterband = target.filterband
        if target.ra_rad is not None:
            self.ra_rad = target.ra_rad
            self.dec_rad = target.dec_rad
            self.alt_rad, self.az_rad, self.pa_rad = self.site.radec2altazpa(self.site.calcLst(self.time),
                                                                             self.ra_rad, self.dec_rad)
        elif target.alt_rad is not None:
            self.alt_rad = target.alt_rad
            self.az_rad = target.az_rad
            self.ra_rad, self.dec_rad, self.pa_rad = self.site.altaz2radecpa(self.site.calcLst(self.time),
                                                                             self.alt_rad, self.az_rad)
        if target.ang_rad is not None:
            self.ang_rad = target.ang_rad
            self.rot_rad = (self.pa_rad - self.ang_rad) % (2 * np.pi)
        elif target.rot_rad is not None:
            self.rot_rad = target.rot_rad
            self.ang_rad = (self.pa_rad - self.rot_rad) % (2 * np.pi)


    def __str__(self):
        """str: The string representation of the instance."""
        return "t=%f ra=%.3f dec=%.3f ang=%.3f filter=%s alt=%.3f "\
               "az=%.3f pa=%.3f rot=%.3f" % \
               (self.time.tai.mjd, self.ra, self.dec, self.ang, self.filterband,
                self.alt, self.az, self.pa, self.rot)

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
