import math

from lsst.ts.observatory.model import ObservatoryPosition

__all__ = ["ObservatoryState"]

class ObservatoryState(ObservatoryPosition):
    """Class for collecting the current state of the observatory.
    """

    def __init__(self, time=0.0, ra_rad=0.0, dec_rad=0.0, ang_rad=0.0,
                 band_filter='r', tracking=False, alt_rad=1.5, az_rad=0.0,
                 pa_rad=0.0, rot_rad=0.0, telalt_rad=1.5, telaz_rad=0.0,
                 telrot_rad=0.0, domalt_rad=1.5, domaz_rad=0.0,
                 mountedfilters=['g', 'r', 'i', 'z', 'y'],
                 unmountedfilters=['u']):
        """Initialize the class.

        Parameters
        ----------
        time : float
            The UTC timestamp (seconds) for the given pointing position
            information.
        ra_rad : float
            The right ascension (radians) for the pointing position.
        dec_rad : float
            The declination (radians) for the pointing position.
        ang_rad : float

        band_filter : str
            The band filter being used during the pointing.
        tracking : bool
            The tracking state of the pointing.
        alt_rad : float
            The altitude (radians) of the pointing.
        az_rad : float
            The azimuth (radians) of the pointing.
        pa_rad : float

        rot_rad : float

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
        """
        ObservatoryPosition.__init__(self, time, ra_rad, dec_rad, ang_rad,
                                     band_filter, tracking, alt_rad, az_rad,
                                     pa_rad, rot_rad)

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
    def domalt(self):
        """float: Return the altitude (degrees) of the dome opening."""
        return math.degrees(self.domalt_rad)

    @property
    def domaz(self):
        """float: Return the azimuth (degrees) of the dome opening."""
        return math.degrees(self.domaz_rad)

    @property
    def telalt(self):
        """float: Return the altitude (degrees) of the telescope."""
        return math.degrees(self.telalt_rad)

    @property
    def telaz(self):
        """float: Return the azimuth (degrees) of the telescope."""
        return math.degrees(self.telaz_rad)

    @property
    def telrot(self):
        """float: Return the rotator angle (degrees) of the telescope."""
        return math.degrees(self.telrot_rad)

    @property
    def domalt_peakspeed(self):
        """float: Return the altitude peak speed (degrees/sec) of the dome
                  opening."""
        return math.degrees(self.domalt_peakspeed_rad)

    @property
    def domaz_peakspeed(self):
        """float: Return the azimuth peak speed (degrees/sec) of the dome
                  opening."""
        return math.degrees(self.domaz_peakspeed_rad)

    @property
    def telalt_peakspeed(self):
        """float: Return the altitude peak speed (degrees/sec) of the
                  telescope."""
        return math.degrees(self.telalt_peakspeed_rad)

    @property
    def telaz_peakspeed(self):
        """float: Return the azimuth peak speed (degrees/sec) of the
                  telescope."""
        return math.degrees(self.telaz_peakspeed_rad)

    @property
    def telrot_peakspeed(self):
        """float: Return the telescope rotator peak speed (degrees/sec)."""
        return math.degrees(self.telrot_peakspeed_rad)

    def __str__(self):
        """str: The string representation of the instance."""
        return "%s telaz=%.3f telrot=%.3f mounted=%s unmounted=%s" % \
               (ObservatoryPosition.__str__(self), self.telaz, self.telrot,
                self.mountedfilters, self.unmountedfilters)

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

    def set_position(self, newposition):
        """Override the current position information with new values.

        This function only overrides the position information in the current
        state. Telescope and dome position information are filled with the
        overriding position information. All peak speeds are set to zero.
        Also, the mounted and unmounted filter lists are unchanged.

        Parameters
        ----------
        newposition : :class:`.ObservatoryState`
            A new observatory state instance from which to set the current
            state information.
        """
        self.time = newposition.time
        self.ra_rad = newposition.ra_rad
        self.dec_rad = newposition.dec_rad
        self.ang_rad = newposition.ang_rad
        self.filter = newposition.filter
        self.tracking = newposition.tracking
        self.alt_rad = newposition.alt_rad
        self.az_rad = newposition.az_rad
        self.pa_rad = newposition.pa_rad
        self.rot_rad = newposition.rot_rad

        self.telalt_rad = newposition.alt_rad
        self.telalt_peakspeed_rad = 0
        self.telaz_rad = newposition.az_rad
        self.telaz_peakspeed_rad = 0
        self.telrot_rad = newposition.rot_rad
        self.telrot_peakspeed_rad = 0
        self.domalt_rad = newposition.alt_rad
        self.domalt_peakspeed_rad = 0
        self.domaz_rad = newposition.az_rad
        self.domaz_peakspeed_rad = 0

    def swap_filter(self, filter_to_mount, filter_to_unmount):
        """Perform a filter swap on the internal lists.

        DEPRECATED?

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
