import math
from astropy.time import Time


__all__ = ["ObservatoryState"]


class ObservatoryState(object):
    """A class describing a complete observatory state (telescope, dome, camera positions and peak speeds).

    Parameters
    ----------
    time : astropy.time.Time
        The time for the telescope state.
    ra_rad : float
        The right ascension (radians) for the pointing.
    dec_rad : float
        The declination (radians) for the pointing.
    ang_rad : float
        ??
    band_filter : str
        The filter currently in use.
    tracking : bool
        The tracking state of the observatory.
    alt_rad : float
        The altitude (radians) of the pointing.
    az_rad : float
        The azimuth (radians) of the pointing.
    pa_rad : float
        The parallactic angle (radians) of the pointing.
    rot_rad : float
        ??
    telalt_rad : float
        The altitude (radians) of the telescope for the given state.
    telaz_rad : float
        The azimuth (radians) of the telescope for the given state.
    telrot_rad : float
        The telescope rotator angle (radians) for the given state.
    domalt_rad : float
        The altitude (radians) of the dome opening for the given state.
    domaz_rad : float
        The azimuth (radians) of the dome opening for the given state.
    mountedfilters : list[str]
        The list of band filters currently mounted for the given state.
    unmountedfilters : list[str]
        The list of band filters currently unmounted for the given state.

    Note: It seems overkill to specify RA/Dec/ang, as well as alt/az/pa/rot
    The reason why both are specified is tied to whether tracking is True or False --
    If tracking is True, then ra/dec is maintained between updates of the state.
    If tracking is False, then alt/az is maintained between updates of the state.
    These updates are not done here, but in the ObservatoryModel.
    """

    def __init__(self, time=0.0,
                 ra_rad=0.0, dec_rad=0.0, ang_rad=0.0,
                 band_filter='r',
                 tracking=False,
                 alt_rad=1.5, az_rad=0.0, pa_rad=0.0, rot_rad=0.0,
                 telalt_rad=1.5, telaz_rad=0.0, telrot_rad=0.0,
                 domalt_rad=1.5, domaz_rad=0.0,
                 mountedfilters=['g', 'r', 'i', 'z', 'y'],
                 unmountedfilters=['u']):
        self.time = time
        self.ra_rad = ra_rad
        self.dec_rad = dec_rad
        self.ang_rad = ang_rad
        self.filter = band_filter
        self.tracking = tracking
        self.alt_rad = alt_rad
        self.az_rad = az_rad
        self.pa_rad = pa_rad
        self.rot_rad = rot_rad

        self.telalt_rad = telalt_rad
        self.telalt_peakspeed_rad = 0
        self.telaz_rad = telaz_rad
        self.telaz_peakspeed_rad = 0
        self.telrot_rad = telrot_rad
        self.telrot_peakspeed_rad = 0
        self.domalt_rad = domalt_rad
        self.domalt_peakspeed_rad = 0
        self.domaz_rad = domaz_rad
        self.domaz_peakspeed_rad = 0
        self.mountedfilters = list(mountedfilters)
        self.unmountedfilters = list(unmountedfilters)

    @property
    def mjd_time(self):
        """float: Return the MJD TAI time of the pointing position."""
        return self.time.tai.mjd

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

    @property
    def domalt(self):
        """float: Return the altitude (degrees) of the dome opening."""
        return math.degrees(self.domalt_rad)

    @property
    def domalt_peakspeed(self):
        """float: Return the altitude peak speed (degrees/sec) of the dome
                  opening."""
        return math.degrees(self.domalt_peakspeed_rad)

    @property
    def domaz(self):
        """float: Return the azimuth (degrees) of the dome opening."""
        return math.degrees(self.domaz_rad)

    @property
    def domaz_peakspeed(self):
        """float: Return the azimuth peak speed (degrees/sec) of the dome
                  opening."""
        return math.degrees(self.domaz_peakspeed_rad)

    @property
    def telalt(self):
        """float: Return the altitude (degrees) of the telescope."""
        return math.degrees(self.telalt_rad)

    @property
    def telalt_peakspeed(self):
        """float: Return the altitude peak speed (degrees/sec) of the
                  telescope."""
        return math.degrees(self.telalt_peakspeed_rad)

    @property
    def telaz(self):
        """float: Return the azimuth (degrees) of the telescope."""
        return math.degrees(self.telaz_rad)

    @property
    def telaz_peakspeed(self):
        """float: Return the azimuth peak speed (degrees/sec) of the
                  telescope."""
        return math.degrees(self.telaz_peakspeed_rad)

    @property
    def telrot(self):
        """float: Return the rotator angle (degrees) of the telescope."""
        return math.degrees(self.telrot_rad)

    @property
    def telrot_peakspeed(self):
        """float: Return the telescope rotator peak speed (degrees/sec)."""
        return math.degrees(self.telrot_peakspeed_rad)

    def __str__(self):
        state = "t=%.1f ra=%.3f dec=%.3f ang=%.3f filter=%s track=%s alt=%.3f "\
                "az=%.3f pa=%.3f rot=%.3f" % (self.time, self.ra, self.dec, self.ang,
                                              self.filter, self.tracking, self.alt, self.az,
                                              self.pa, self.rot)
        state += " telaz=%.3f telrot=%.3f mounted=%s unmounted=%s"\
                 % (self.telaz, self.telrot, self.mountedfilters, self.unmountedfilters)
        return state

    def set(self, newstate):
        """Override the current state information with new values.

        Parameters
        ----------
        newstate : :class:`.ObservatoryState`
            A new observatory state instance from which to set the current
            state information.
        """
        self.time = newstate.time
        self.ra_rad = newstate.ra_rad
        self.dec_rad = newstate.dec_rad
        self.ang_rad = newstate.ang_rad
        self.filter = newstate.filter
        self.tracking = newstate.tracking
        self.alt_rad = newstate.alt_rad
        self.az_rad = newstate.az_rad
        self.pa_rad = newstate.pa_rad
        self.rot_rad = newstate.rot_rad

        self.telalt_rad = newstate.telalt_rad
        self.telalt_peakspeed_rad = newstate.telalt_peakspeed_rad
        self.telaz_rad = newstate.telaz_rad
        self.telaz_peakspeed_rad = newstate.telaz_peakspeed_rad
        self.telrot_rad = newstate.telrot_rad
        self.telrot_peakspeed_rad = newstate.telrot_peakspeed_rad
        self.domalt_rad = newstate.domalt_rad
        self.domalt_peakspeed_rad = newstate.domalt_peakspeed_rad
        self.domaz_rad = newstate.domaz_rad
        self.domaz_peakspeed_rad = newstate.domaz_peakspeed_rad
        self.mountedfilters = list(newstate.mountedfilters)
        self.unmountedfilters = list(newstate.unmountedfilters)

    def mount_filter(self, filter_to_mount, filter_to_unmount):
        """Swap the filters mounted on the camera.

        Parameters
        ----------
        filter_to_mount : str
            The name of the band filter to mount.
        filter_to_unmount : str
            The name of the band filter to unmount.
        """
        self.mountedfilters.remove(filter_to_unmount)
        self.unmountedfilters.remove(filter_to_mount)
        self.mountedfilters.append(filter_to_mount)
        self.unmountedfilters.append(filter_to_unmount)
