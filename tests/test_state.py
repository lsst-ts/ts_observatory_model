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
import unittest

from lsst.ts.observatory.model import ObservatoryState


class ObservatoryStateTest(unittest.TestCase):
    def setUp(self):
        self.obs_state_default = ObservatoryState()

        self.ra_truth = 41.010349
        self.dec_truth = -19.985964
        self.ang_truth = 175.993874013319
        self.alt_truth = 79.6715648342188
        self.az_truth = 353.018554127083
        self.pa_truth = 173.584814234084
        self.rot_truth = -2.40905977923582
        self.telalt_truth = 79.6715648342188
        self.telaz_truth = -6.98144587291673
        self.telrot_truth = -2.40905977923582
        self.domalt_truth = 79.6715648342188
        self.domaz_truth = -6.98144587291673
        self.telalt_peakspeed_truth = -3.5
        self.telaz_peakspeed_truth = -5.52367616573824
        self.telrot_peakspeed_truth = 0.0
        self.domalt_peakspeed_truth = -1.75
        self.domaz_peakspeed_truth = -1.5

        self.timestamp = 1672534239.91224
        self.ra_rad_truth = math.radians(self.ra_truth)
        self.dec_rad_truth = math.radians(self.dec_truth)
        self.ang_rad_truth = math.radians(self.ang_truth)
        self.band_filter_truth = "y"
        self.tracking_truth = True
        self.alt_rad_truth = math.radians(self.alt_truth)
        self.az_rad_truth = math.radians(self.az_truth)
        self.pa_rad_truth = math.radians(self.pa_truth)
        self.rot_rad_truth = math.radians(self.rot_truth)
        self.telalt_rad_truth = math.radians(self.telalt_truth)
        self.telaz_rad_truth = math.radians(self.telaz_truth)
        self.telrot_rad_truth = math.radians(self.telrot_truth)
        self.domalt_rad_truth = math.radians(self.domalt_truth)
        self.domaz_rad_truth = math.radians(self.domaz_truth)
        self.telalt_peakspeed_rad_truth = math.radians(self.telalt_peakspeed_truth)
        self.telaz_peakspeed_rad_truth = math.radians(self.telaz_peakspeed_truth)
        self.telrot_peakspeed_rad_truth = math.radians(self.telrot_peakspeed_truth)
        self.domalt_peakspeed_rad_truth = math.radians(self.domalt_peakspeed_truth)
        self.domaz_peakspeed_rad_truth = math.radians(self.domaz_peakspeed_truth)
        self.mounted_filters_truth = ["g", "r", "i", "y", "u"]
        self.unmounted_filters_truth = ["z"]

        self.obs_state_new = ObservatoryState(
            self.timestamp,
            self.ra_rad_truth,
            self.dec_rad_truth,
            self.ang_rad_truth,
            self.band_filter_truth,
            self.tracking_truth,
            self.alt_rad_truth,
            self.az_rad_truth,
            self.pa_rad_truth,
            self.rot_rad_truth,
            self.telalt_rad_truth,
            self.telaz_rad_truth,
            self.telrot_rad_truth,
            self.domalt_rad_truth,
            self.domaz_rad_truth,
            self.mounted_filters_truth,
            self.unmounted_filters_truth,
        )
        self.obs_state_new.telalt_peakspeed_rad = self.telalt_peakspeed_rad_truth
        self.obs_state_new.telaz_peakspeed_rad = self.telaz_peakspeed_rad_truth
        self.obs_state_new.telrot_peakspeed_rad = self.telrot_peakspeed_rad_truth
        self.obs_state_new.domalt_peakspeed_rad = self.domalt_peakspeed_rad_truth
        self.obs_state_new.domaz_peakspeed_rad = self.domaz_peakspeed_rad_truth

    def check_observatory_state(self, obs_state, position_only=False):
        self.assertEqual(obs_state.time, self.timestamp)
        self.assertEqual(obs_state.ra, self.ra_truth)
        self.assertEqual(obs_state.dec, self.dec_truth)
        self.assertEqual(obs_state.ang, self.ang_truth)
        self.assertEqual(obs_state.filter, self.band_filter_truth)
        self.assertTrue(obs_state.tracking)
        self.assertEqual(obs_state.alt, self.alt_truth)
        self.assertEqual(obs_state.az, self.az_truth)
        self.assertEqual(obs_state.pa, self.pa_truth)
        self.assertEqual(obs_state.rot, self.rot_truth)
        if not position_only:
            self.assertEqual(obs_state.telalt, self.telalt_truth)
            self.assertEqual(obs_state.telaz, self.telaz_truth)
            self.assertEqual(obs_state.telrot, self.telrot_truth)
            self.assertEqual(obs_state.domalt, self.domalt_truth)
            self.assertEqual(obs_state.domaz, self.domaz_truth)
            self.assertEqual(obs_state.telalt_peakspeed, self.telalt_peakspeed_truth)
            self.assertEqual(obs_state.telaz_peakspeed, self.telaz_peakspeed_truth)
            self.assertEqual(obs_state.telrot_peakspeed, self.telrot_peakspeed_truth)
            self.assertEqual(obs_state.domalt_peakspeed, self.domalt_peakspeed_truth)
            self.assertAlmostEqual(
                obs_state.domaz_peakspeed, self.domaz_peakspeed_truth, places=1
            )
            self.assertListEqual(obs_state.mountedfilters, self.mounted_filters_truth)
            self.assertListEqual(
                obs_state.unmountedfilters, self.unmounted_filters_truth
            )
        else:
            self.assertEqual(obs_state.telalt, self.alt_truth)
            self.assertEqual(obs_state.telaz, self.az_truth)
            self.assertEqual(obs_state.telrot, self.rot_truth)
            self.assertEqual(obs_state.domalt, self.alt_truth)
            self.assertEqual(obs_state.domaz, self.az_truth)
            self.assertEqual(obs_state.telalt_peakspeed, 0.0)
            self.assertEqual(obs_state.telaz_peakspeed, 0.0)
            self.assertEqual(obs_state.telrot_peakspeed, 0.0)
            self.assertEqual(obs_state.domalt_peakspeed, 0.0)
            self.assertEqual(obs_state.domaz_peakspeed, 0.0)
            self.assertListEqual(obs_state.mountedfilters, ["g", "r", "i", "z", "y"])
            self.assertListEqual(obs_state.unmountedfilters, ["u"])

    def test_basic_information_after_default_creation(self):
        self.assertEqual(self.obs_state_default.time, 0.0)
        self.assertEqual(self.obs_state_default.ra_rad, 0.0)
        self.assertEqual(self.obs_state_default.dec_rad, 0.0)
        self.assertEqual(self.obs_state_default.ang_rad, 0.0)
        self.assertEqual(self.obs_state_default.filter, "r")
        self.assertFalse(self.obs_state_default.tracking)
        self.assertEqual(self.obs_state_default.alt_rad, 1.5)
        self.assertEqual(self.obs_state_default.az_rad, 0.0)
        self.assertEqual(self.obs_state_default.pa_rad, 0.0)
        self.assertEqual(self.obs_state_default.rot_rad, 0.0)
        self.assertEqual(self.obs_state_default.telalt_rad, 1.5)
        self.assertEqual(self.obs_state_default.telaz_rad, 0.0)
        self.assertEqual(self.obs_state_default.telrot_rad, 0.0)
        self.assertEqual(self.obs_state_default.domalt_rad, 1.5)
        self.assertEqual(self.obs_state_default.domaz_rad, 0.0)
        self.assertListEqual(
            self.obs_state_default.mountedfilters, ["g", "r", "i", "z", "y"]
        )
        self.assertListEqual(self.obs_state_default.unmountedfilters, ["u"])

    def test_string_representation(self):
        truth_str = (
            "t=0.0 ra=0.000 dec=0.000 ang=0.000 filter=r "
            "track=False alt=85.944 az=0.000 pa=0.000 rot=0.000 "
            "telaz=0.000 telrot=0.000 "
            "mounted=['g', 'r', 'i', 'z', 'y'] "
            "unmounted=['u']"
        )
        self.assertEqual(str(self.obs_state_default), truth_str)

    def test_state_set(self):
        self.obs_state_default.set(self.obs_state_new)
        self.check_observatory_state(self.obs_state_default)

    def test_state_set_position(self):
        self.obs_state_default.set_position(self.obs_state_new)
        self.check_observatory_state(self.obs_state_default, position_only=True)

    def test_swap_filter(self):
        self.obs_state_default.swap_filter("u", "z")
        self.assertListEqual(
            self.obs_state_default.mountedfilters, self.mounted_filters_truth
        )
        self.assertListEqual(
            self.obs_state_default.unmountedfilters, self.unmounted_filters_truth
        )


if __name__ == "__main__":
    unittest.main()
