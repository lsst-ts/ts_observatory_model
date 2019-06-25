import math
import palpy as pal
from lsst.sims.utils import Site

__all__ = ['get_closest_angle_distance', 'SiteUtils']

TWOPI = 2 * math.pi

def get_closest_angle_distance(target_rad, current_abs_rad,
                               min_abs_rad=None, max_abs_rad=None,
                               wrap_padding=0.0):
    """Calculate the closest angular distance including handling cable wrap if needed.
    Can provide a padding parameter, to avoid getting too close to the wrap limits.
    Returns both the "accumulated angle" -- i.e. final angle including distance -- and the distance traveled.

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
    wrap_padding : float, optional
        The amount of padding to use to make sure we don't track into limits (radians).
        Default is 0 - no padding.
        However, a value of 0.873 (50 degrees) is useful for the *telescope azimuth*, as the
        total range for this is -270/+270 and this will let you offset significantly from the limit.

    Returns
    -------
    tuple(float, float)
        (accumulated angle in radians, distance angle in radians)
    """
    # if there are specified wrap limits, normalizes the target angle.
    # Note that this erases the history of the total "accumulated" angle.
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
        if accum_abs_rad > max_abs_rad - wrap_padding:
            distance_rad = distance_rad - TWOPI
        if accum_abs_rad < min_abs_rad + wrap_padding:
            distance_rad = distance_rad + TWOPI

    # compute final accumulated angle
    final_abs_rad = current_abs_rad + distance_rad
    return (final_abs_rad, distance_rad)


class SiteUtils(object):
    """A utility function that (for a given lsst.sims.utils.Site object) calculates
    the LST at a given time, and converts between ra/dec to approximate alt/az (without refraction?).

    Parameters
    ----------
    site : lsst.sims.utils.Site, opt
        The location of the observatory. Default = Site('LSST').
    """
    def __init__(self, site=None):
        if site is None:
            self.site = Site('LSST')
        else:
            self.site = site

    def calcLst(self, time):
        """Calculate local sidereal time (in radians) for a given time.

        Parameters
        ----------
        time : astropy.time.Time

        Returns
        -------
        float
            local sidereal time
        """
        lst = pal.gmst(time.ut1.mjd) + self.site.longitude_rad
        lst = lst % (2.0 * math.pi)
        return lst


    def altaz2radecpa(self, lst_rad, alt_rad, az_rad):
        """Converts alt, az coordinates into ra, dec for the given time.

        Parameters
        ----------
        lst_rad : float
            The local sidereal time in radians
        alt_rad : float
            The altitude in radians
        az_rad : float
            The azimuth in radians

        Returns
        -------
        tuple(float, float, float)
            (right ascension in radians, declination in radians, parallactic angle in radians)
        """
        (ha_rad, dec_rad) = pal.dh2e(az_rad, alt_rad, self.site.latitude_rad)
        pa_rad = divmod(pal.pa(ha_rad, dec_rad, self.site.latitude_rad), TWOPI)[1]
        ra_rad = divmod(lst_rad - ha_rad, TWOPI)[1]
        return (ra_rad, dec_rad, pa_rad)


    def radec2altazpa(self, lst_rad, ra_rad, dec_rad):
        """Converts ra, de coordinates into alt, az for given time.

        Parameters
        ----------
        lst_rad : float
            The local sidereal time in radians
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
        ha_rad = lst_rad - ra_rad
        (az_rad, alt_rad) = pal.de2h(ha_rad, dec_rad, self.site.latitude_rad)
        pa_rad = divmod(pal.pa(ha_rad, dec_rad, self.site.latitude_rad), TWOPI)[1]
        return (alt_rad, az_rad, pa_rad)