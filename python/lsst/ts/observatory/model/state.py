# This file is part of ts_observatory_model.
#
# Developed for the Vera Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License

import math

from lsst.ts.observatory.model import ObservatoryPosition

__all__ = ["ObservatoryState"]


class ObservatoryState(ObservatoryPosition):
    """Class for collecting the current state of the observatory."""

    def __init__(
        self,
        time=0.0,
        ra_rad=0.0,
        dec_rad=0.0,
        ang_rad=0.0,
        band_filter="r",
        tracking=False,
        alt_rad=1.5,
        az_rad=0.0,
        pa_rad=0.0,
        rot_rad=0.0,
        telalt_rad=1.5,
        telaz_rad=0.0,
        telrot_rad=0.0,
        domalt_rad=1.5,
        domaz_rad=0.0,
        mountedfilters=["g", "r", "i", "z", "y"],
        unmountedfilters=["u"],
    ):
        """Initialize the class.

        Parameters
        ----------
        time : `float`
            The UTC timestamp (seconds) for the given pointing position
            information.
        ra_rad : `float`
            The right ascension (radians) for the pointing position.
        dec_rad : `float`
            The declination (radians) for the pointing position.
        ang_rad : `float`

        band_filter : `str`
            The band filter being used during the pointing.
        tracking : `bool`
            The tracking state of the pointing.
        alt_rad : `float`
            The altitude (radians) of the pointing.
        az_rad : `float`
            The azimuth (radians) of the pointing.
        pa_rad : `float`
            The parallactic angle (radians) of the pointing.
        rot_rad : `float`

        telalt_rad : `float`
            The altitude (radians) of the telescope for the given state.
        telaz_rad : `float`
            The azimuth (radians) of the telescope for the given state.
        telrot_rad : `float`
            The telescope rotator angle (radians) for the given state.
        domalt_rad : `float`
            The altitude (radians) of the dome opening for the given state.
        domaz_rad : `float`
            The azimuth (radians) of the dome opening for the given state.
        mountedfilters : `list` of `str`
            The list of band filters currently mounted for the given state.
        unmountedfilters : `list` of `str`
            The list of band filters currently unmounted for the given state.
        fail_record : `dict`
            A dictionary of string keys that represent reason of failure, and
            and integer to record the count of that failure.
        fail_state : `int`
            A unique integer to define the type of target failure that occured.
        fail_value_table : `dict`
            Table used to calculate the fail state.
            ___  ___  ___  ___  ___  ___
             |    |    |    |    |    |
            rot  rot  az   az   alt  alt
            min  max  max  min  max  min
        """
        ObservatoryPosition.__init__(
            self,
            time,
            ra_rad,
            dec_rad,
            ang_rad,
            band_filter,
            tracking,
            alt_rad,
            az_rad,
            pa_rad,
            rot_rad,
        )

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
        self.fail_record = {}
        self.fail_state = 0
        self.fail_value_table = {
            "altEmax": 1,
            "altEmin": 2,
            "azEmax": 4,
            "azEmin": 8,
            "rotEmax": 16,
            "rotEmin": 32,
            "filter": 64,
        }

    def __str__(self):
        """str: The string representation of the instance."""
        return "%s telaz=%.3f telrot=%.3f mounted=%s unmounted=%s" % (
            ObservatoryPosition.__str__(self),
            self.telaz,
            self.telrot,
            self.mountedfilters,
            self.unmountedfilters,
        )

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

        UNUSED/DEPRECATED?

        Parameters
        ----------
        filter_to_mount : `str`
            The name of the band filter to mount.
        filter_to_unmount : `str`
            The name of the band filter to unmount.
        """
        self.mountedfilters.remove(filter_to_unmount)
        self.unmountedfilters.remove(filter_to_mount)
        self.mountedfilters.append(filter_to_mount)
        self.unmountedfilters.append(filter_to_unmount)
