import math
import unittest

from lsst.ts.observatory.model import ObservatoryModelParameters
import lsst.utils.tests

class ObservatoryModelParametersTest(unittest.TestCase):

    def setUp(self):
        self.params = ObservatoryModelParameters()

    def test_some_basic_information_after_creation(self):
        self.assertEqual(self.params.telalt_minpos_rad, 0.0)
        self.assertEqual(self.params.telaz_maxpos_rad, 0.0)
        self.assertFalse(self.params.rotator_followsky)
        self.assertEqual(self.params.filter_darktime, "u")
        self.assertListEqual(self.params.filter_init_unmounted_list, [])
        self.assertDictEqual(self.params.prerequisites, {})

    def test_configure_telescope(self):
        truth = {
            "telescope": {
                "altitude_minpos": 15.0,
                "altitude_maxpos": 85.0,
                "azimuth_minpos": -90.0,
                "azimuth_maxpos": 90.0,
                "altitude_maxspeed": 10.0,
                "altitude_accel": 3.0,
                "altitude_decel": 3.0,
                "azimuth_maxspeed": 8.0,
                "azimuth_accel": 2.0,
                "azimuth_decel": 2.0,
                "settle_time": 1.0
            }
        }
        self.params.configure_telescope(truth)
        self.assertEqual(self.params.telalt_minpos_rad,
                         math.radians(truth["telescope"]["altitude_minpos"]))
        self.assertEqual(self.params.telalt_maxpos_rad,
                         math.radians(truth["telescope"]["altitude_maxpos"]))
        self.assertEqual(self.params.telaz_minpos_rad,
                         math.radians(truth["telescope"]["azimuth_minpos"]))
        self.assertEqual(self.params.telaz_maxpos_rad,
                         math.radians(truth["telescope"]["azimuth_maxpos"]))
        self.assertEqual(self.params.telalt_maxspeed_rad,
                         math.radians(truth["telescope"]["altitude_maxspeed"]))
        self.assertEqual(self.params.telalt_accel_rad,
                         math.radians(truth["telescope"]["altitude_accel"]))
        self.assertEqual(self.params.telalt_decel_rad,
                         math.radians(truth["telescope"]["altitude_decel"]))
        self.assertEqual(self.params.telaz_maxspeed_rad,
                         math.radians(truth["telescope"]["azimuth_maxspeed"]))
        self.assertEqual(self.params.telaz_accel_rad,
                         math.radians(truth["telescope"]["azimuth_accel"]))
        self.assertEqual(self.params.telaz_decel_rad,
                         math.radians(truth["telescope"]["azimuth_decel"]))
        self.assertEqual(self.params.mount_settletime,
                         truth["telescope"]["settle_time"])

    def test_configure_rotator(self):
        truth = {
            "rotator": {
                "minpos": -90.0,
                "maxpos": 90.0,
                "maxspeed": 4.0,
                "accel": 1.0,
                "decel": 1.0,
                "filter_change_pos": 45.0,
                "follow_sky": True,
                "resume_angle": False
            }
        }
        self.params.configure_rotator(truth)
        self.assertEqual(self.params.telrot_minpos_rad,
                         math.radians(truth["rotator"]["minpos"]))
        self.assertEqual(self.params.telrot_maxpos_rad,
                         math.radians(truth["rotator"]["maxpos"]))
        self.assertEqual(self.params.telrot_maxspeed_rad,
                         math.radians(truth["rotator"]["maxspeed"]))
        self.assertEqual(self.params.telrot_accel_rad,
                         math.radians(truth["rotator"]["accel"]))
        self.assertEqual(self.params.telrot_decel_rad,
                         math.radians(truth["rotator"]["decel"]))
        self.assertEqual(self.params.telrot_filterchangepos_rad,
                         math.radians(truth["rotator"]["filter_change_pos"]))
        self.assertTrue(self.params.rotator_followsky)
        self.assertFalse(self.params.rotator_resumeangle)

    def test_configure_dome(self):
        truth = {
            "dome": {
                "altitude_maxspeed": 6.0,
                "altitude_accel": 1.5,
                "altitude_decel": 1.5,
                "altitude_freerange": 0.,
                "azimuth_maxspeed": 4.0,
                "azimuth_accel": 0.5,
                "azimuth_decel": 0.5,
                "azimuth_freerange": 0.,
                "settle_time": 3.0
            }
        }
        self.params.configure_dome(truth)
        self.assertEqual(self.params.domalt_maxspeed_rad,
                         math.radians(truth["dome"]["altitude_maxspeed"]))
        self.assertEqual(self.params.domalt_accel_rad,
                         math.radians(truth["dome"]["altitude_accel"]))
        self.assertEqual(self.params.domalt_decel_rad,
                         math.radians(truth["dome"]["altitude_decel"]))
        self.assertEqual(self.params.domaz_maxspeed_rad,
                         math.radians(truth["dome"]["azimuth_maxspeed"]))
        self.assertEqual(self.params.domaz_accel_rad,
                         math.radians(truth["dome"]["azimuth_accel"]))
        self.assertEqual(self.params.domaz_decel_rad,
                         math.radians(truth["dome"]["azimuth_decel"]))
        self.assertEqual(self.params.domaz_settletime,
                         truth["dome"]["settle_time"])

    def test_configure_optics(self):
        truth = {
            "optics_loop_corr": {
                "tel_optics_ol_slope": 3.0 / 2.0,
                "tel_optics_cl_delay": [0.0, 34.0],
                "tel_optics_cl_alt_limit": [0.0, 7.0, 90.0]
            }
        }
        self.params.configure_optics(truth)
        olc = truth["optics_loop_corr"]
        self.assertEqual(self.params.optics_ol_slope,
                         olc["tel_optics_ol_slope"] / math.radians(1))
        self.assertListEqual(self.params.optics_cl_delay,
                             olc["tel_optics_cl_delay"])
        olc_altlims = [math.radians(x) for x in olc["tel_optics_cl_alt_limit"]]
        self.assertListEqual(self.params.optics_cl_altlimit, olc_altlims)

    def test_configure_camera(self):
        truth = {
            "camera": {
                "readout_time": 2.0,
                "shutter_time": 1.0,
                "filter_change_time": 90.0,
                "filter_removable": ['y', 'z'],
                "filter_max_changes_burst_num": 10,
                "filter_max_changes_burst_time": 20 * 60.0,
                "filter_max_changes_avg_num": 2000,
                "filter_max_changes_avg_time": 365 * 24 * 60 * 60.0,
                "filter_mounted": ['g', 'r', 'i', 'z', 'y'],
                "filter_unmounted": ['u']
            }
        }
        self.params.configure_camera(truth)
        cam = truth["camera"]
        self.assertEqual(self.params.readouttime, cam["readout_time"])
        self.assertEqual(self.params.shuttertime, cam["shutter_time"])
        self.assertEqual(self.params.filter_changetime,
                         cam["filter_change_time"])
        self.assertListEqual(self.params.filter_removable_list,
                             cam["filter_removable"])
        self.assertEqual(self.params.filter_max_changes_burst_num,
                         cam["filter_max_changes_burst_num"])
        self.assertEqual(self.params.filter_max_changes_burst_time,
                         cam["filter_max_changes_burst_time"])
        self.assertEqual(self.params.filter_max_changes_avg_num,
                         cam["filter_max_changes_avg_num"])
        self.assertEqual(self.params.filter_max_changes_avg_time,
                         cam["filter_max_changes_avg_time"])
        ratio = cam["filter_max_changes_avg_time"] /\
            cam["filter_max_changes_avg_num"]
        self.assertEqual(self.params.filter_max_changes_avg_interval,
                         ratio)
        self.assertListEqual(self.params.filter_init_mounted_list,
                             cam["filter_mounted"])
        self.assertListEqual(self.params.filter_init_unmounted_list,
                             cam["filter_unmounted"])

        truth["camera"]["filter_max_changes_avg_num"] = 0
        self.params.configure_camera(truth)
        self.assertEqual(self.params.filter_max_changes_avg_interval,
                         0.0)

    def test_configure_slew(self):
        truth_activities = ["telalt", "telaz", "domalt", "domaz",
                            "telopticsclosedloop", "exposures"]
        truth = {
            "slew": {
                "prereq_telalt": [],
                "prereq_telaz": [],
                "prereq_domalt": [],
                "prereq_domaz": [],
                "prereq_exposures": ["telopticsclosedloop"],
                "prereq_telopticsclosedloop": ["domalt", "domazsettle",
                                               "telsettle", "readout",
                                               "telopticsopenloop",
                                               "filter", "telrot"]
            }
        }
        self.params.configure_slew(truth, truth_activities)
        slew = truth["slew"]
        self.assertListEqual(self.params.prerequisites["telalt"],
                             slew["prereq_telalt"])
        self.assertListEqual(self.params.prerequisites["telaz"],
                             slew["prereq_telaz"])
        self.assertListEqual(self.params.prerequisites["domalt"],
                             slew["prereq_domalt"])
        self.assertListEqual(self.params.prerequisites["domaz"],
                             slew["prereq_domaz"])
        self.assertListEqual(self.params.prerequisites["exposures"],
                             slew["prereq_exposures"])
        self.assertListEqual(self.params.prerequisites["telopticsclosedloop"],
                             slew["prereq_telopticsclosedloop"])

class MemoryTestClass(lsst.utils.tests.MemoryTestCase):
    pass

def setup_module(module):
    lsst.utils.tests.init()

if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
