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

__all__ = ["ObservatoryPosition"]


class ObservatoryPosition(object):
    """Class for providing base pointing position information."""

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

        """
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

    def __str__(self):
        """str: The string representation of the instance."""
        return (
            "t=%.1f ra=%.3f dec=%.3f ang=%.3f filter=%s track=%s alt=%.3f "
            "az=%.3f pa=%.3f rot=%.3f"
            % (
                self.time,
                self.ra,
                self.dec,
                self.ang,
                self.filter,
                self.tracking,
                self.alt,
                self.az,
                self.pa,
                self.rot,
            )
        )

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
