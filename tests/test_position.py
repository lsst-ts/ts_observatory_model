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

from lsst.ts.observatory.model import ObservatoryPosition


class ObservatoryPositionTest(unittest.TestCase):
    def setUp(self):
        self.ra_truth = 41.010349
        self.dec_truth = -19.985964
        self.ang_truth = 175.993874013319
        self.alt_truth = 79.6715648342188
        self.az_truth = 353.018554127083
        self.pa_truth = 173.584814234084
        self.rot_truth = -2.40905977923582

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

        self.op = ObservatoryPosition(
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
        )

    def test_basic_information_after_creation(self):
        self.assertEqual(self.op.time, self.timestamp)
        self.assertEqual(self.op.ra, self.ra_truth)
        self.assertEqual(self.op.dec, self.dec_truth)
        self.assertEqual(self.op.ang, self.ang_truth)
        self.assertEqual(self.op.filter, self.band_filter_truth)
        self.assertTrue(self.op.tracking)
        self.assertEqual(self.op.alt, self.alt_truth)
        self.assertEqual(self.op.az, self.az_truth)
        self.assertEqual(self.op.pa, self.pa_truth)
        self.assertEqual(self.op.rot, self.rot_truth)

    def test_string_representation(self):
        instance_srep = (
            "t=1672534239.9 ra=41.010 dec=-19.986 "
            "ang=175.994 filter=y track=True alt=79.672 "
            "az=353.019 pa=173.585 rot=-2.409"
        )
        self.assertEqual(str(self.op), instance_srep)


if __name__ == "__main__":
    unittest.main()
