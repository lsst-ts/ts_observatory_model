import math
import numpy as np
from astropy.time import Time, TimeDelta
import unittest

from lsst.ts.observatory.model import Config, ObservatoryModel, ObservatoryState, Target
import lsst.utils.tests

class ObservatoryModelTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.start_time = Time('2022-10-01')
        cls.config = Config()
        # Configure with default configuration parameters.
        cls.model = ObservatoryModel(cls.start_time, config=cls.config)

    def setUp(self):
        self.model.park_state.filterband = "r"
        self.model.reset()

    def test_init(self):
        temp_model = ObservatoryModel(self.start_time)
        self.assertIsNotNone(temp_model.log)
        self.assertAlmostEqual(temp_model.conf.site.longitude_rad, -1.23480, delta=1e6)
        self.assertEqual(temp_model.current_state.telalt_rad,
                         math.radians(temp_model.conf.park.telescope_altitude))

    def test_configure(self):
        temp_model = ObservatoryModel(self.start_time, config=self.config)
        # site properties come from lsst.sims.utils.Site('LSST')
        self.assertEqual(temp_model.conf.site.longitude_rad, math.radians(-70.7494))
        self.assertEqual(temp_model.conf.site.longitude, -70.7494)
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
        self.model.time = self.start_time
        self.model.configure(self.config)
        self.model.reset()
        expected = "t=59853.000428 ra=0.000 dec=0.000 ang=0.000 filter=r track=False " \
                   "alt=86.500 az=0.000 pa=0.000 rot=0.000 telaz=0.000 telrot=0.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)

    def test_update(self):
        self.model.time = self.start_time
        self.model.configure(self.config)
        self.model.update_state(self.start_time + TimeDelta(3000))
        expected = "t=62853.000428 ra=15.903 dec=-26.744 ang=180.000 filter=r track=False " \
                   "alt=86.500 az=0.000 pa=180.000 rot=0.000 telaz=0.000 telrot=0.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)

    def test_slew_altaz(self):
        self.model.time = self.start_time
        self.model.configure(self.config)

        t = self.start_time
        expected = "t=59853.000428 ra=298.961 dec=-26.744 ang=180.000 filter=r " \
                   "track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 " \
                   "telaz=0.000 telrot=0.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)

        self.model.slew_altaz(t, math.radians(80), math.radians(0), math.radians(0), "r")
        self.model.start_tracking(t)
        t = t + TimeDelta(7.7)
        expected =  "t=59959.357571 ra=172.363 dec=-20.244 ang=0.000 filter=r " \
                    "track=True alt=80.000 az=0.000 pa=180.000 rot=-180.000 " \
                    "telaz=0.000 telrot=-360.000 " \
                    "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)

        t = self.start_time + TimeDelta(100.)
        self.model.update_state(t)
        expected = "t=59959.357571 ra=172.363 dec=-20.244 ang=0.000 filter=r " \
                   "track=False alt=80.000 az=-0.000 pa=180.000 rot=180.000 " \
                   "telaz=0.000 telrot=-90.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)

        self.model.slew_altaz(t, math.radians(70), math.radians(30), math.radians(15), "r")
        self.model.start_tracking(t)
        expected = "t=60071.714714 ra=61.769 dec=-12.558 ang=11.265 filter=r " \
                   "track=True alt=70.000 az=30.000 pa=206.265 rot=-165.000 " \
                   "telaz=30.000 telrot=-345.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)

    def test_slew_radec(self):
        t = self.start_time
        self.model.time = t
        self.model.configure(self.config)

        expected = "t=59853.000428 ra=298.961 dec=-26.744 ang=180.000 filter=r " \
                   "track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 " \
                   "telaz=0.000 telrot=0.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)

        self.model.slew_radec(t, math.radians(80), math.radians(0), math.radians(0), "r")
        expected = "t=59968.612314 ra=80.000 dec=0.000 ang=317.161 filter=r " \
                   "track=False alt=-57.255 az=155.044 pa=201.376 rot=244.215 " \
                   "telaz=155.044 telrot=-90.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)

        t = self.start_time + TimeDelta(100)
        self.model.update_state(t)
        expected = "t=59968.612314 ra=80.000 dec=-0.000 ang=317.161 filter=r " \
                   "track=False alt=-57.255 az=155.044 pa=201.376 rot=244.215 " \
                   "telaz=155.044 telrot=-90.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)

        self.model.slew_radec(t, math.radians(70), math.radians(-30), math.radians(15), "r")
        expected = "t=59972.851646 ra=70.000 dec=-30.000 ang=292.210 filter=r " \
                   "track=False alt=33.403 az=107.987 pa=251.582 rot=319.372 " \
                   "telaz=107.987 telrot=-90.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)

    def test_get_approximateSlewTime(self):
        self.model.time = self.start_time
        self.model.configure(self.config)

        alt = np.array([self.model.current_state.telalt_rad])
        az = np.array([self.model.current_state.telaz_rad])
        f = self.model.current_state.filterband
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

    def test_get_slew_delay(self):
        self.model.time = self.start_time
        self.model.configure(self.config)
        expected = "t=59853.000428 ra=298.961 dec=-26.744 ang=180.000 filter=r " \
                   "track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 " \
                   "telaz=0.000 telrot=0.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)

        target = Target()
        target.ra_rad = math.radians(240)
        target.dec_rad = math.radians(-30)
        target.ang_rad = math.radians(0)
        target.filterband = "r"

        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 104.726, delta=1e-3)

        self.model.slew(target)

        target = Target()
        target.ra_rad = math.radians(240)
        target.dec_rad = math.radians(-30)
        target.ang_rad = math.radians(0)
        target.filterband = "g"

        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 120, delta=1e-3)

        target = Target()
        target.ra_rad = math.radians(240)
        target.dec_rad = math.radians(-30)
        target.ang_rad = math.radians(10)
        target.filterband = "r"

        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 2.0, delta=1e-3)

        self.model.slew(target)
        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 106.18 , delta=1e-3)

        target.ang_rad = math.radians(15)
        delay, status = self.model.get_slew_delay(target)
        self.assertAlmostEqual(delay, 2.0, delta=1e-3)

    def test_slew(self):
        self.model.time = self.start_time
        self.model.configure(self.config)

        target = Target()
        target.ra_rad = math.radians(240)
        target.dec_rad = math.radians(-30)
        target.ang_rad = math.radians(0)
        target.filterband = "r"

        self.model.slew(target)
        expected ="t=59957.726408 ra=240.000 dec=-30.000 ang=196.089 filter=r " \
                  "track=False alt=35.820 az=252.964 pa=107.492 rot=271.403 " \
                  "telaz=-107.036 telrot=-90.000 " \
                  "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)

        target = Target()
        target.ra_rad = math.radians(245)
        target.dec_rad = math.radians(-20)
        target.ang_rad = math.radians(0)
        target.filterband = "i"

        self.model.slew(target)
        expected = "t=60077.726408 ra=245.000 dec=-20.000 ang=203.414 filter=i " \
                   "track=False alt=-39.662 az=183.890 pa=176.424 rot=333.010 " \
                   "telaz=-176.110 telrot=-90.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)

    def test_domecrawl(self):
        temp_model = ObservatoryModel(self.start_time)

        target = Target()
        target.ra_rad = math.radians(280)
        target.dec_rad = math.radians(-20)
        target.ang_rad = math.radians(0)
        target.filterband = "r"

        # Just test whether dome crawl is faster or not.
        # If we test the final slew state, this is including other aspects of slew model (such as CLoptics).
        temp_model.conf.domerad['azimuth_freerange_rad'] = 0
        delay_nocrawl = temp_model.get_slew_delay(target)
        temp_model.conf.domerad['azimuth_freerange_rad'] = np.radians(4.0)
        delay_crawl = temp_model.get_slew_delay(target)
        self.assertTrue( delay_crawl < delay_nocrawl)

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

    def test_slewdata(self):
        self.model.time = self.start_time
        self.model.configure(self.config)

        target = Target()
        target.ra_rad = math.radians(60)
        target.dec_rad = math.radians(-40)
        target.ang_rad = math.radians(0)
        target.filterband = "r"

        self.model.slew(target)
        critical_path = ['telopticsclosedloop', 'domazsettle', 'domaz']
        delays_dict = {'telalt': 19.999999999999996, 'telaz': 20.85281661752584,
                       'telrot': 29.21428571428571, 'telsettle': 3.0,
                       'telopticsopenloop': 19.0, 'telopticsclosedloop': 36.0,
                       'domalt': 41.99999999999999, 'domaz': 89.97981088178724,
                       'domazsettle': 1.0, 'readout': 2.0}
        self.check_delay_and_state(self.model,
                                   delays_dict,
                                   critical_path,
                                   (-3.5, 7.0, -3.5, -1.75, 1.500))

        target = Target()
        target.ra_rad = math.radians(60)
        target.dec_rad = math.radians(-40)
        target.ang_rad = math.radians(0)
        target.filterband = "i"

        self.model.slew(target)
        expected = "t=60099.980239 ra=60.000 dec=-40.000 ang=0.000 filter=i track=False " \
                   "alt=2.450 az=223.962 pa=128.478 rot=128.478 telaz=223.962 telrot=-90.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)
        delays_dict = {'telrot': 85.13556888620646, 'filter': 120.0, 'readout': 2.0}
        self.check_delay_and_state(self.model,
                                   delays_dict,
                                   ['filter'],
                                   [0.0, 0.0, -3.5, 0.0, 1.5000000000000002])

        target = Target()
        target.ra_rad = math.radians(61)
        target.dec_rad = math.radians(-21)
        target.ang_rad = math.radians(1)
        target.filterband = "i"

        self.model.slew(target)
        expected = "t=60108.674474 ra=61.000 dec=-21.000 ang=217.124 filter=i track=False " \
                   "alt=75.358 az=306.196 pa=131.690 rot=274.566 telaz=270.000 telrot=-90.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected)
        delays_dict = {'telaz': 3.2201931073212853, 'telsettle': 3.0,
                       'domaz': 7.694234500832666,
                       'domazsettle': 1.0, 'readout': 2.0}
        self.check_delay_and_state(self.model,
                                   delays_dict,
                                   ['domazsettle', 'domaz'],
                                   [0.0, 7.0, 0.0, 0.0, 1.50])

    def test_rotator(self):
        self.model.time = self.start_time
        self.model.configure(self.config)

        self.model.slew_radec(self.start_time, math.radians(80), math.radians(0), math.radians(0), "r")
        expected = "t=59968.612314 ra=80.000 dec=0.000 ang=317.161 filter=r track=False " \
                   "alt=-57.255 az=155.044 pa=201.376 rot=244.215 telaz=155.044 telrot=-90.000 " \
                   "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), "t=68.0 ra=80.000 dec=0.000 ang=180.000 "
                         "filter=r track=True alt=33.540 az=67.263 pa=232.821 rot=52.821 "
                         "telaz=67.263 telrot=52.821 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")
        self.model.slew_radec(0, math.radians(83.5), math.radians(0), math.radians(0), "r")
        self.assertEqual(str(self.model.current_state), "t=72.8 ra=83.500 dec=0.000 ang=180.000 "
                         "filter=r track=True alt=30.744 az=69.709 pa=234.123 rot=54.123 "
                         "telaz=69.709 telrot=54.123 "
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']")

    def test_unmount_filter(self):
        # Make sure reset to original config/expected filters.
        self.model.time = self.start_time
        self.model.configure(self.config)
        expected_state = "t=59853.000428 ra=298.961 dec=-26.744 ang=180.000 filter=r " \
                         "track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 telaz=0.000 telrot=0.000 " \
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        park_state = "t=59853.000428 ra=0.000 dec=0.000 ang=0.000 filter=r " \
                     "track=False alt=86.500 az=0.000 pa=0.000 rot=0.000 telaz=0.000 telrot=0.000 " \
                     "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected_state)
        self.assertEqual(str(self.model.park_state), park_state)
        self.model.unmount_filter("z")
        expected_state = "t=59853.000428 ra=298.961 dec=-26.744 ang=180.000 filter=r track=False " \
                         "alt=86.500 az=0.000 pa=180.000 rot=0.000 telaz=0.000 telrot=0.000 " \
                         "mounted=['g', 'r', 'i', 'y', 'u'] unmounted=['z']"
        park_state = "t=59853.000428 ra=0.000 dec=0.000 ang=0.000 filter=r track=False " \
                     "alt=86.500 az=0.000 pa=0.000 rot=0.000 telaz=0.000 telrot=0.000 " \
                     "mounted=['g', 'r', 'i', 'y', 'u'] unmounted=['z']"
        self.assertEqual(str(self.model.current_state), expected_state)
        self.assertEqual(str(self.model.park_state), park_state)
        self.model.unmount_filter("u")
        expected_state = "t=59853.000428 ra=298.961 dec=-26.744 ang=180.000 filter=r " \
                         "track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 telaz=0.000 telrot=0.000 " \
                         "mounted=['g', 'r', 'i', 'y', 'z'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected_state)

    def test_park(self):
        self.model.time = self.start_time
        self.model.configure(self.config)
        # Start at park, slew to target.
        # Use default configuration (dome crawl, CL updates, etc.)
        target = Target()
        target.ra_rad = math.radians(60)
        target.dec_rad = math.radians(-20)
        target.ang_rad = math.radians(0)
        target.filterband = "z"

        self.model.slew(target)

        self.model.park()
        expected_state = "t=60230.956351 ra=295.624 dec=-26.744 ang=180.000 filter=z track=False " \
                         "alt=86.500 az=0.000 pa=180.000 rot=0.000 telaz=0.000 telrot=0.000 " \
                         "mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']"
        self.assertEqual(str(self.model.current_state), expected_state)

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


class MemoryTestClass(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
