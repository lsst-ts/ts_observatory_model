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
import numpy as np
import unittest

from lsst.ts.dateloc import ObservatoryLocation
from lsst.ts.observatory.model import ObservatoryModel, Target
import lsst.utils.tests

class ObservatoryModelTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.location = ObservatoryLocation()
        cls.location.for_lsst()

        cls.model = ObservatoryModel(cls.location)
        cls.model.configure_from_module()

    def setUp(self):
        self.model.park_state.filter = "r"
        self.model.reset()

    def check_delay_and_state(self, model, delays, critical_path, state):
        lastslew_delays_dict = model.lastslew_delays_dict
        for key in lastslew_delays_dict:
            # This activity was not recorded in truth arrays.
            if key == "telsettle":
                continue
            self.assertAlmostEqual(lastslew_delays_dict[key], delays[key],
                                   delta=1e-3)

        self.assertListEqual(model.lastslew_criticalpath, critical_path)

        self.assertAlmostEqual(model.current_state.telalt_peakspeed,
                                state[0], delta=1e-3)
        self.assertAlmostEqual(model.current_state.telaz_peakspeed,
                                state[1], delta=1e-3)
        self.assertAlmostEqual(model.current_state.telrot_peakspeed,
                                 state[2], delta=1e-3)
        self.assertAlmostEqual(model.current_state.domalt_peakspeed,
                                state[3], delta=1e-3)
        self.assertAlmostEqual(model.current_state.domaz_peakspeed,
                                state[4], delta=1e-3)

    def make_slewact_dict(self, delays):
        slewacts = ("telalt", "telaz", "telrot", "telopticsopenloop",
                    "telopticsclosedloop", "domalt", "domaz", "domazsettle",
                    "filter", "readout")
        delay_map = {}
        for i, slew in enumerate(slewacts):
            if delays[i] > 0.0:
                delay_map[slew] = delays[i]
        return delay_map

    def test_init(self):
        temp_model = ObservatoryModel(self.location)
        self.assertIsNotNone(temp_model.log)
        self.assertAlmostEqual(temp_model.location.longitude_rad, -1.23480, delta=1e6)
        self.assertEqual(temp_model.current_state.telalt_rad, 1.5)

    def test_configure(self):
        temp_model = ObservatoryModel(self.location)
        temp_model.configure_from_module()

        self.assertEqual(temp_model.location.longitude_rad, math.radians(-70.7494))
        self.assertEqual(temp_model.location.longitude, -70.7494)
        self.assertEqual(temp_model.current_state.telalt_rad, math.radians(86.5))

    def test_get_closest_angle_distance_unlimited(self):
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(0), math.radians(0)),
                         (math.radians(0), math.radians(0)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(90), math.radians(0)),
                         (math.radians(90), math.radians(90)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(180), math.radians(0)),
                         (math.radians(180), math.radians(180)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(360), math.radians(0)),
                         (math.radians(0), math.radians(0)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-90), math.radians(0)),
                         (math.radians(-90), math.radians(-90)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-180), math.radians(0)),
                         (math.radians(180), math.radians(180)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-360), math.radians(0)),
                         (math.radians(0), math.radians(0)))

    def test_get_closest_angle_distance_cable_wrap270(self):
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(0), math.radians(0),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(0), math.radians(0)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(90), math.radians(0),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(90), math.radians(90)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(180), math.radians(0),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(180), math.radians(180)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(360), math.radians(0),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(0), math.radians(0)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-90), math.radians(0),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(-90), math.radians(-90)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-180), math.radians(0),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(180), math.radians(180)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-360), math.radians(0),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(0), math.radians(0)))

        self.assertEqual(self.model.get_closest_angle_distance(math.radians(0), math.radians(180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(0), math.radians(-180)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(90), math.radians(180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(90), math.radians(-90)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(180), math.radians(180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(180), math.radians(0)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(360), math.radians(180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(0), math.radians(-180)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-90), math.radians(180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(270), math.radians(90)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-180), math.radians(180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(180), math.radians(0)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-360), math.radians(180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(0), math.radians(-180)))

        self.assertEqual(self.model.get_closest_angle_distance(math.radians(0), math.radians(-180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(0), math.radians(180)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(90), math.radians(-180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(-270), math.radians(-90)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(180), math.radians(-180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(-180), math.radians(0)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(360), math.radians(-180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(0), math.radians(180)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-90), math.radians(-180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(-90), math.radians(90)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-180), math.radians(-180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(-180), math.radians(0)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-360), math.radians(-180),
                                                               math.radians(-270), math.radians(270)),
                         (math.radians(0), math.radians(180)))

    def test_get_closest_angle_distance_cable_wrap90(self):
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(0), math.radians(0),
                                                               math.radians(-90), math.radians(90)),
                         (math.radians(0), math.radians(0)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(45), math.radians(0),
                                                               math.radians(-90), math.radians(90)),
                         (math.radians(45), math.radians(45)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(90), math.radians(0),
                                                               math.radians(-90), math.radians(90)),
                         (math.radians(90), math.radians(90)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(180), math.radians(0),
                                                               math.radians(-90), math.radians(90)),
                         (math.radians(0), math.radians(0)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(270), math.radians(0),
                                                               math.radians(-90), math.radians(90)),
                         (math.radians(-90), math.radians(-90)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(360), math.radians(0),
                                                               math.radians(-90), math.radians(90)),
                         (math.radians(0), math.radians(0)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-45), math.radians(0),
                                                               math.radians(-90), math.radians(90)),
                         (math.radians(-45), math.radians(-45)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-90), math.radians(0),
                                                               math.radians(-90), math.radians(90)),
                         (math.radians(-90), math.radians(-90)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-180), math.radians(0),
                                                               math.radians(-90), math.radians(90)),
                         (math.radians(0), math.radians(0)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-270), math.radians(0),
                                                               math.radians(-90), math.radians(90)),
                         (math.radians(90), math.radians(90)))
        self.assertEqual(self.model.get_closest_angle_distance(math.radians(-360), math.radians(0),
                                                               math.radians(-90), math.radians(90)),
                         (math.radians(0), math.radians(0)))

    def test_reset(self):
        self.model.reset()
        self.assertEqual(str(self.model.current_state), "t=0.0 ra=0.000 dec=0.000 ang=0.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=0.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")

    def test_slew_altaz(self):
        self.model.update_state(0)
        # Use old values, to avoid updating final states.
        self.model.params.domaz_free_range = 0
        self.model.params.optics_cl_delay = [0, 20.0]

        self.assertEqual(str(self.model.current_state), "t=0.0 ra=29.480 dec=-26.744 ang=180.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.model.slew_altaz(0, math.radians(80), math.radians(0), math.radians(0), "r")
        self.model.start_tracking(0)
        self.assertEqual(str(self.model.current_state), "t=7.7 ra=29.510 dec=-20.244 ang=180.000 "
                         "filter=r track=True alt=80.000 az=0.000 pa=180.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")

        self.model.update_state(100)
        self.assertEqual(str(self.model.current_state), "t=100.0 ra=29.510 dec=-20.244 ang=180.000 "
                         "filter=r track=True alt=79.994 az=357.901 pa=178.068 rot=358.068 "
                         "telaz=-2.099 telrot=-1.932 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.model.slew_altaz(100, math.radians(70), math.radians(30), math.radians(15), "r")
        self.model.start_tracking(0)
        self.assertEqual(str(self.model.current_state), "t=144.4 ra=40.172 dec=-12.558 ang=191.265 "
                         "filter=r track=True alt=70.000 az=30.000 pa=206.265 rot=15.000 "
                         "telaz=30.000 telrot=15.000 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")

    def test_slew_radec(self):
        self.model.update_state(0)
        # Use old values, to avoid updating final states.
        self.model.params.domaz_free_range = 0
        self.model.params.optics_cl_delay = [0, 20.0]
        self.model.params.rotator_followsky = True
        self.assertEqual(str(self.model.current_state), "t=0.0 ra=29.480 dec=-26.744 ang=180.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.model.slew_radec(0, math.radians(80), math.radians(0), math.radians(0), "r")
        self.assertEqual(str(self.model.current_state), "t=68.0 ra=80.000 dec=0.000 ang=180.000 "
                         "filter=r track=True alt=33.540 az=67.263 pa=232.821 rot=52.821 "
                         "telaz=67.263 telrot=52.821 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")

        self.model.update_state(100)
        self.assertEqual(str(self.model.current_state), "t=100.0 ra=80.000 dec=0.000 ang=180.000 "
                         "filter=r track=True alt=33.650 az=67.163 pa=232.766 rot=52.766 "
                         "telaz=67.163 telrot=52.766 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.model.slew_radec(100, math.radians(70), math.radians(-30), math.radians(15), "r")
        self.assertEqual(str(self.model.current_state), "t=144.9 ra=70.000 dec=-30.000 ang=195.000 "
                         "filter=r track=True alt=55.654 az=99.940 pa=259.282 rot=64.282 "
                         "telaz=99.940 telrot=64.282 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")

    def test_get_slew_delay(self):
        self.model.update_state(0)
        # Use old values, to avoid updating final states.
        self.model.params.rotator_followsky = True

        self.assertEqual(str(self.model.current_state), "t=0.0 ra=29.480 dec=-26.744 ang=180.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        # This slew will include a CL optics correction.
        target = Target()
        target.ra_rad = math.radians(60)
        target.dec_rad = math.radians(-20)
        target.ang_rad = math.radians(0)
        target.filter = "r"

        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 85.507, delta=1e-3)

        self.model.slew(target)

        # This slew simply includes a filter change.
        target = Target()
        target.ra_rad = math.radians(60)
        target.dec_rad = math.radians(-20)
        target.ang_rad = math.radians(0)
        target.filter = "g"

        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 120, delta=1e-3)

        # This slew does not include OL correction, but does involve dome crawl.
        target = Target()
        target.ra_rad = math.radians(50)
        target.dec_rad = math.radians(-10)
        target.ang_rad = math.radians(10)
        target.filter = "r"

        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 17.913, delta=1e-3)

        # This slew is only readout.
        self.model.slew(target)
        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 2.0, delta=1e-3)

        # This slew involves rotator.
        target.ang_rad = math.radians(15)
        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 4.472, delta=1e-3)

    def test_get_approximateSlewTime(self):
        self.model.update_state(0)
        alt = np.array([self.model.current_state.telalt_rad])
        az = np.array([self.model.current_state.telaz_rad])
        f = self.model.current_state.filter
        # Check that slew time is == readout time for no motion
        slewtime = self.model.get_approximate_slew_delay(alt, az, f)
        self.assertEqual(slewtime, 2.0)
        # Check that slew time is == filter change time for filter change
        newfilter = 'u'
        if f == newfilter:
            newfilter = 'g'
        slewtime = self.model.get_approximate_slew_delay(alt, az, newfilter)
        self.assertEqual(slewtime, 120.0)
        # Check that get nan when attempting to slew out of bounds
        alt = np.array([np.radians(90), np.radians(0), np.radians(-20)], float)
        az = np.zeros(len(alt), float)
        slewtime = self.model.get_approximate_slew_delay(alt, az, f)
        self.assertTrue(np.all(slewtime < 0))
        # Check that we can calculate slew times with an array.
        alt = np.radians(np.arange(0, 90, 1))
        az = np.radians(np.arange(0, 180, 2))
        slewtime = self.model.get_approximate_slew_delay(alt, az, f)
        self.assertEqual(len(slewtime), len(alt))


    def test_get_slew_delay_followsky_false(self):
        # Test slew time without followsky option. Similar to test_get_slew_delay above.
        self.model.update_state(0)
        self.model.params.rotator_followsky = False
        expected_state = "t=0.0 ra=29.480 dec=-26.744 ang=180.000 " \
                         "filter=r track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 " \
                         "telaz=0.000 telrot=0.000 " \
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected_state)

        target = Target()
        target.ra_rad = math.radians(60)
        target.dec_rad = math.radians(-20)
        target.ang_rad = math.radians(0)
        target.filter = "r"

        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 85.507, delta=1e-3)

        self.model.slew(target)

        target = Target()
        target.ra_rad = math.radians(60)
        target.dec_rad = math.radians(-20)
        target.ang_rad = math.radians(0)
        target.filter = "g"

        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 120, delta=1e-3)

        target = Target()
        target.ra_rad = math.radians(50)
        target.dec_rad = math.radians(-10)
        target.ang_rad = math.radians(10)
        target.filter = "r"

        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 17.913, delta=1e-3)

        self.model.slew(target)
        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 2.0, delta=1e-3)

        # Here is the difference when using followsky = False
        target.ang_rad = math.radians(15)
        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 2.0, delta=1e-3)

    def test_slew(self):
        self.model.update_state(0)
        self.model.params.domaz_free_range = 0
        self.model.params.optics_cl_delay = [0, 20.0]
        self.model.params.rotator_followsky = True

        self.assertEqual(str(self.model.current_state), "t=0.0 ra=29.480 dec=-26.744 ang=180.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")

        target = Target()
        target.ra_rad = math.radians(60)
        target.dec_rad = math.radians(-20)
        target.ang_rad = math.radians(0)
        target.filter = "r"

        self.model.slew(target)
        self.assertEqual(str(self.model.current_state), "t=74.2 ra=60.000 dec=-20.000 ang=180.000 "
                         "filter=r track=True alt=60.904 az=76.495 pa=243.368 rot=63.368 "
                         "telaz=76.495 telrot=63.368 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")

        target = Target()
        target.ra_rad = math.radians(60)
        target.dec_rad = math.radians(-20)
        target.ang_rad = math.radians(0)
        target.filter = "i"

        self.model.slew(target)
        self.assertEqual(str(self.model.current_state), "t=194.2 ra=60.000 dec=-20.000 ang=180.000 "
                         "filter=i track=True alt=61.324 az=76.056 pa=243.156 rot=63.156 "
                         "telaz=76.056 telrot=63.156 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")

    def test_domecrawl(self):
        self.model.update_state(0)
        self.assertEqual(str(self.model.current_state), "t=0.0 ra=29.480 dec=-26.744 ang=180.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")

        target = Target()
        target.ra_rad = math.radians(35)
        target.dec_rad = math.radians(-27)
        target.ang_rad = math.radians(0)
        target.filter = "r"

        # Just test whether dome crawl is faster or not.
        # If we test the final slew state, this is including other aspects of slew model (such as CLoptics).
        self.model.params.domaz_free_range = 0
        delay_nocrawl = self.model.get_slew_delay(target)
        self.model.params.domaz_free_range = np.radians(4.0)
        delay_crawl = self.model.get_slew_delay(target)
        self.assertTrue( delay_crawl < delay_nocrawl)


    def test_slewdata(self):
        self.model.update_state(0)
        # Use old values, to avoid updating final states.
        self.model.params.domaz_free_range = 0
        self.model.params.optics_cl_delay = [0, 20.0]
        self.model.params.rotator_followsky = True

        target = Target()
        target.ra_rad = math.radians(60)
        target.dec_rad = math.radians(-20)
        target.ang_rad = math.radians(0)
        target.filter = "r"

        self.model.slew(target)
        self.assertEqual(str(self.model.current_state), "t=74.2 ra=60.000 dec=-20.000 ang=180.000 "
                         "filter=r track=True alt=60.904 az=76.495 pa=243.368 rot=63.368 "
                         "telaz=76.495 telrot=63.368 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.check_delay_and_state(self.model,
                                   self.make_slewact_dict((8.387, 11.966, 21.641, 7.387, 20.0,
                                                           18.775, 53.174, 1.0, 0.0, 2.0)),
                                   ['telopticsclosedloop', 'domazsettle',
                                    'domaz'],
                                   (-3.50, 7.00, 3.50, -1.75, 1.50))

        target = Target()
        target.ra_rad = math.radians(60)
        target.dec_rad = math.radians(-20)
        target.ang_rad = math.radians(0)
        target.filter = "i"

        self.model.slew(target)
        self.assertEqual(str(self.model.current_state), "t=194.2 ra=60.000 dec=-20.000 ang=180.000 "
                         "filter=i track=True alt=61.324 az=76.056 pa=243.156 rot=63.156 "
                         "telaz=76.056 telrot=63.156 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.check_delay_and_state(self.model,
                                   self.make_slewact_dict((0.0, 0.0, 0.0, 0.0,
                                                           0.0, 0.0, 0.0, 0.0,
                                                           120.0, 2.0)),
                                   ['filter'],
                                   (0, 0, 0, 0, 0))

        target = Target()
        target.ra_rad = math.radians(61)
        target.dec_rad = math.radians(-21)
        target.ang_rad = math.radians(1)
        target.filter = "i"

        self.model.slew(target)
        self.assertEqual(str(self.model.current_state), "t=199.0 ra=61.000 dec=-21.000 ang=181.000 "
                         "filter=i track=True alt=60.931 az=78.751 pa=245.172 rot=64.172 "
                         "telaz=78.751 telrot=64.172 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.check_delay_and_state(self.model,
                                   self.make_slewact_dict((0.683, 1.244,
                                                           2.022, 0.117,
                                                           0.0, 1.365,
                                                           3.801, 1.0,
                                                           0.000, 2.000)),
                                   ['domazsettle', 'domaz'],
                                   (-1.194, 4.354, 1.011, -0.598, 1.425))

    def test_rotator_followsky_true(self):
        # Use old values, to avoid updating final states.
        self.model.params.domaz_free_range = 0
        self.model.params.optics_cl_delay = [0, 20.0]

        self.model.update_state(0)
        self.model.params.rotator_followsky = True
        self.assertEqual(str(self.model.current_state), "t=0.0 ra=29.480 dec=-26.744 ang=180.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.model.slew_radec(0, math.radians(80), math.radians(0), math.radians(0), "r")
        self.assertEqual(str(self.model.current_state), "t=68.0 ra=80.000 dec=0.000 ang=180.000 "
                         "filter=r track=True alt=33.540 az=67.263 pa=232.821 rot=52.821 "
                         "telaz=67.263 telrot=52.821 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.model.slew_radec(0, math.radians(83.5), math.radians(0), math.radians(0), "r")
        self.assertEqual(str(self.model.current_state), "t=72.8 ra=83.500 dec=0.000 ang=180.000 "
                         "filter=r track=True alt=30.744 az=69.709 pa=234.123 rot=54.123 "
                         "telaz=69.709 telrot=54.123 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")

    def test_rotator_followsky_false(self):
        # Use old values, to avoid updating final states.
        self.model.update_state(0)
        self.model.params.domaz_free_range = 0
        self.model.params.optics_cl_delay = [0, 20.0]
        self.model.params.rotator_followsky = False
        self.assertEqual(str(self.model.current_state), "t=0.0 ra=29.480 dec=-26.744 ang=180.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.model.slew_radec(0, math.radians(80), math.radians(0), math.radians(0), "r")
        self.assertEqual(str(self.model.current_state), "t=68.0 ra=80.000 dec=0.000 ang=232.933 "
                         "filter=r track=True alt=33.540 az=67.263 pa=232.821 rot=359.888 "
                         "telaz=67.263 telrot=-0.112 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.model.slew_radec(0, math.radians(83.5), math.radians(0), math.radians(0), "r")
        self.assertEqual(str(self.model.current_state), "t=72.8 ra=83.500 dec=0.000 ang=234.241 "
                         "filter=r track=True alt=30.744 az=69.709 pa=234.123 rot=359.881 "
                         "telaz=69.709 telrot=-0.119 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")



    def test_swap_filter(self):
        # Use old values, to avoid updating final states.
        self.model.params.domaz_free_range = 0
        self.model.params.optics_cl_delay = [0, 20.0]
        self.model.params.rotator_followsky = True
        self.model.update_state(0)
        self.assertEqual(str(self.model.current_state), "t=0.0 ra=29.480 dec=-26.744 ang=180.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.assertEqual(str(self.model.park_state), "t=0.0 ra=0.000 dec=0.000 ang=0.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=0.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.model.swap_filter("z")
        self.assertEqual(str(self.model.current_state), "t=0.0 ra=29.480 dec=-26.744 ang=180.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'y', 'u'] unmounted=['z']")
        self.assertEqual(str(self.model.park_state), "t=0.0 ra=0.000 dec=0.000 ang=0.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=0.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'y', 'u'] unmounted=['z']")
        self.model.swap_filter("u")
        self.assertEqual(str(self.model.current_state), "t=0.0 ra=29.480 dec=-26.744 ang=180.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'y', 'z'] unmounted=['u']")
        self.assertEqual(str(self.model.park_state), "t=0.0 ra=0.000 dec=0.000 ang=0.000 "
                         "filter=r track=False alt=86.500 az=0.000 pa=0.000 rot=0.000 "
                         "telaz=0.000 telrot=0.000 "
                         "mounted=['g', 'r', 'i', 'y', 'z'] unmounted=['u']")

    def test_park(self):
        self.model.update_state(0)
        self.model.params.rotator_followsky = False
        self.model.params.rotator_resume_angle = False
        # Start at park, slew to target.
        # Use default configuration (dome crawl, CL updates, etc.)
        target = Target()
        target.ra_rad = math.radians(60)
        target.dec_rad = math.radians(-20)
        target.ang_rad = math.radians(0)
        target.filter = "z"

        self.model.slew(target)
        expected_state = "t=156.0 ra=60.000 dec=-20.000 ang=243.495 filter=z track=True " \
                         "alt=61.191 az=76.196 pa=243.224 rot=359.729 telaz=76.196 telrot=-0.271 " \
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected_state)
        self.check_delay_and_state(self.model,
                                   self.make_slewact_dict((8.387, 11.966, 0.0,
                                                           7.387, 36.0, 18.775,
                                                           48.507, 1.0, 120.0,
                                                           2.0)),
                                   ['telopticsclosedloop', 'filter'],
                                   (-3.50, 7.00, 0.0, -1.75, 1.50))

        self.model.park()
        expected_state = "t=241.1 ra=30.487 dec=-26.744 ang=180.000 filter=z track=False " \
                         "alt=86.500 az=0.000 pa=180.000 rot=0.000 telaz=0.000 telrot=0.000 " \
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected_state)
        self.check_delay_and_state(self.model,
                                   self.make_slewact_dict((8.231, 11.885,
                                                           1.041, 7.231, 36.0,
                                                           18.462, 48.130,
                                                           1.0, 0.0, 2.0)),
                                   ['telopticsclosedloop', 'domazsettle',
                                    'domaz'],
                                   (3.50, -7.00, 0.520, 1.75, -1.50))


    def test_get_deep_drilling_time(self):
        target = Target()
        target.is_deep_drilling = True
        target.is_dd_firstvisit = True
        target.remaining_dd_visits = 96
        target.dd_exposures = 2 * 96
        target.dd_filterchanges = 3
        target.dd_exptime = 96 * 2 * 15.0

        ddtime = self.model.get_deep_drilling_time(target)
        self.assertEqual(ddtime, 3808.0)


    def test_get_configure_dict(self):
        cd = ObservatoryModel.get_configure_dict()
        self.assertEqual(len(cd), 7)
        self.assertEqual(len(cd["telescope"]), 11)
        self.assertEqual(len(cd["camera"]), 10)


class MemoryTestClass(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
