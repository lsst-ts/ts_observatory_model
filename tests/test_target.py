import collections
import math
import unittest

from lsst.ts.observatory.model import Target
import lsst.utils.tests

class TargetTest(unittest.TestCase):

    def setUp(self):
        self.targetId = 3
        self.filterband = 'r'
        self.ra = 300.518929
        self.dec = -1.720965
        self.ang = 45.0
        self.num_exposures = 2
        self.exposure_times = [15.0, 15.0]

        self.alt = 45.0
        self.az = 225.0
        self.rot = 30.0

        self.ra_rad = math.radians(self.ra)
        self.dec_rad = math.radians(self.dec)
        self.ang_rad = math.radians(self.ang)
        self.alt_rad = math.radians(self.alt)
        self.az_rad = math.radians(self.az)
        self.rot_rad = math.radians(self.rot)

        self.target = Target(self.targetId, self.filterband,
                             ra_rad=self.ra_rad, dec_rad=self.dec_rad, ang_rad=self.ang_rad,
                             num_exp=self.num_exposures, exp_times=self.exposure_times)

    def test_exceptions(self):
        # Test that get expected exception if fail to set any of ra/dec or alt/az
        self.assertRaises(ValueError, Target, targetid=self.targetId, filterband=self.filterband,
                          ra_rad=None, dec_rad=None, ang_rad=self.ang_rad,
                          num_exp=self.num_exposures, exp_times=self.exposure_times)
        # Test that you get expected exception if you define ra but not dec.
        self.assertRaises(ValueError, Target, targetid=self.targetId, filterband=self.filterband,
                          ra_rad=self.ra_rad, dec_rad=None, ang_rad=self.ang_rad,
                          num_exp=self.num_exposures, exp_times=self.exposure_times)
        # Test that you get expected exception if you define alt but not az.
        self.assertRaises(ValueError, Target, targetid=self.targetId, filterband=self.filterband,
                          alt_rad=self.alt_rad, az_rad=None, rot_rad=self.ang_rad,
                          num_exp=self.num_exposures, exp_times=self.exposure_times)
        # Test that you get expected exception if num_exp != length of exp_times
        self.assertRaises(ValueError, Target, targetid=self.targetId, filterband=self.filterband,
                          ra_rad=self.ra_rad, dec_rad=self.dec_rad, ang_rad=self.ang_rad,
                          num_exp=1, exp_times=self.exposure_times)

    def test_basic_information_after_creation(self):
        target = Target(self.targetId, self.filterband,
                        ra_rad=self.ra_rad, dec_rad=self.dec_rad, ang_rad=self.ang_rad,
                        num_exp=self.num_exposures, exp_times=self.exposure_times)
        self.assertEqual(target.targetid, self.targetId)
        self.assertEqual(target.filterband, self.filterband)
        self.assertEqual(target.ra, self.ra)
        self.assertEqual(target.dec, self.dec)
        self.assertEqual(target.num_exp, self.num_exposures)
        self.assertListEqual(target.exp_times, self.exposure_times)
        self.assertEqual(target.total_exp_time, sum(self.exposure_times))

    def test_json_serialization(self):
        jsondump = self.target.to_json()
        target2 = Target(0, None, 0, 0)
        target2.from_json(jsondump)
        self.assertEqual(self.target.targetid, target2.targetid)
        self.assertEqual(self.target.filterband, target2.filterband)
        self.assertEqual(self.target.ra_rad, target2.ra_rad)
        self.assertEqual(self.target.dec_rad, target2.dec_rad)
        self.assertEqual(self.target.num_exp, target2.num_exp)
        self.assertListEqual(self.target.exp_times, target2.exp_times)

    def test_json_ingest_has_required_params(self):
        self.assertRaises(KeyError, self.init_target_with_bad_json)

    def init_target_with_bad_json(self):
        missingfilter = '{"targetid": 3, "ra_rad": 5.24504477561707, "dec_rad": -0.030036505561584215, "ang_rad": 0.7853981633974483, "num_exp": 2, "exp_times": [15.0, 15.0], "_exp_time": null, "time": 0.0, "airmass": 0.0, "sky_brightness": 0.0, "cloud": 0.0, "seeing": 0.0, "propid": 0, "need": 0.0, "bonus": 0.0, "value": 0.0, "goal": 0, "visits": 0, "progress": 0.0, "sequenceid": 0, "subsequencename": "", "groupid": 0, "groupix": 0, "is_deep_drilling": false, "is_dd_firstvisit": false, "remaining_dd_visits": 0, "dd_exposures": 0, "dd_filterchanges": 0, "dd_exptime": 0.0, "alt_rad": 0.7853981633974483, "az_rad": 3.9269908169872414, "rot_rad": 0.5235987755982988, "telalt_rad": 0.7853981633974483, "telaz_rad": 3.9269908169872414, "telrot_rad": 0.5235987755982988, "propboost": 1.0, "slewtime": 0.0, "cost": 0.0, "rank": 0.0, "num_props": 0, "propid_list": [], "need_list": [], "bonus_list": [], "value_list": [], "propboost_list": [], "sequenceid_list": [], "subsequencename_list": [], "groupid_list": [], "groupix_list": [], "is_deep_drilling_list": [], "is_dd_firstvisit_list": [], "remaining_dd_visits_list": [], "dd_exposures_list": [], "dd_filterchanges_list": [], "dd_exptime_list": [], "last_visit_time": 0.0, "note": ""}'
        t = Target(0, None, 0, 0)
        t.from_json(missingfilter)

    def test_string_representation(self):
        target_str = 'targetid 3 filterband r numexp 2 exp_times [15.0, 15.0] ' \
                     'ra 300.518929 dec -1.720965 ang 45.0 alt None az None rot None'
        self.assertEqual(str(self.target), target_str)

    def test_creation_from_topic(self):
        topic = collections.namedtuple('topic', ['targetId',
                                                 'filter', 'ra', 'decl',
                                                 'skyAngle',
                                                 'numExposures',
                                                 'exposureTimes'])
        topic.targetId = 1
        topic.filter = 'z'
        topic.ra = 274.279376
        topic.decl = -14.441534
        topic.skyAngle = 45.0
        topic.numExposures = 3
        topic.exposureTimes = [5.0, 10.0, 5.0]
        target = Target.from_topic(topic)
        self.assertEqual(target.targetid, topic.targetId)
        self.assertEqual(target.filterband, topic.filter)
        self.assertEqual(target.ra, topic.ra)
        self.assertAlmostEqual(target.dec, topic.decl, delta=1e-7)
        self.assertEqual(target.num_exp, topic.numExposures)
        self.assertListEqual(target.exp_times, topic.exposureTimes)

class MemoryTestClass(lsst.utils.tests.MemoryTestCase):
    pass

def setup_module(module):
    lsst.utils.tests.init()

if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
