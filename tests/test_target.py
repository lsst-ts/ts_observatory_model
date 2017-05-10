import collections
import math
import unittest

from lsst.ts.observatory.model import Target
import lsst.utils.tests

class TargetTest(unittest.TestCase):

    def setUp(self):
        self.targetId = 3
        self.fieldId = 2573
        self.band_filter = 'r'
        self.ra = 300.518929
        self.dec = -1.720965
        self.ang = 45.0
        self.num_exposures = 2
        self.exposure_times = [15.0, 15.0]

        self.ra_rad = math.radians(self.ra)
        self.dec_rad = math.radians(self.dec)
        self.ang_rad = math.radians(self.ang)

        self.target = Target(self.targetId, self.fieldId, self.band_filter,
                             self.ra_rad, self.dec_rad, self.ang_rad,
                             self.num_exposures, self.exposure_times)

    def test_basic_information_after_creation(self):
        self.assertEqual(self.target.targetid, self.targetId)
        self.assertEqual(self.target.fieldid, self.fieldId)
        self.assertEqual(self.target.filter, self.band_filter)
        self.assertEqual(self.target.ra, self.ra)
        self.assertEqual(self.target.dec, self.dec)
        self.assertEqual(self.target.num_exp, self.num_exposures)
        self.assertListEqual(self.target.exp_times, self.exposure_times)

    def test_string_representation(self):
        truth_str = "targetid=3 field=2573 filter=r exp_times=[15.0, 15.0] "\
                    "ra=300.519 dec=-1.721 ang=45.000 alt=0.000 az=0.000 "\
                    "rot=0.000 telalt=0.000 telaz=0.000 telrot=0.000 "\
                    "time=0.0 airmass=0.000 brightness=0.000 "\
                    "cloud=0.00 seeing=0.00 visits=0 progress=0.00% "\
                    "seqid=0 ssname= groupid=0 groupix=0 "\
                    "firstdd=False ddvisits=0 "\
                    "need=0.000 bonus=0.000 value=0.000 propboost=1.000 "\
                    "propid=[] need=[] bonus=[] value=[] propboost=[] "\
                    "slewtime=0.000 cost=0.000 rank=0.000"
        self.assertEqual(str(self.target), truth_str)

    def test_copy_creation(self):
        target2 = self.target.get_copy()
        target2.targetid = 10
        target2.fieldid = 2142
        self.assertEqual(self.target.targetid, self.targetId)
        self.assertEqual(target2.targetid, 10)
        self.assertEqual(self.target.fieldid, self.fieldId)
        self.assertEqual(target2.fieldid, 2142)

    def test_creation_from_topic(self):
        topic = collections.namedtuple('topic', ['targetId', 'fieldId',
                                                 'filter', 'ra', 'dec',
                                                 'angle',
                                                 'num_exposures',
                                                 'exposure_times'])
        topic.targetId = 1
        topic.fieldId = 2000
        topic.filter = 'z'
        topic.ra = 274.279376
        topic.dec = -14.441534
        topic.angle = 45.0
        topic.num_exposures = 3
        topic.exposure_times = [5.0, 10.0, 5.0]
        target = Target.from_topic(topic)
        self.assertEqual(target.targetid, topic.targetId)
        self.assertEqual(target.fieldid, topic.fieldId)
        self.assertEqual(target.filter, topic.filter)
        self.assertEqual(target.ra, topic.ra)
        self.assertAlmostEqual(target.dec, topic.dec, delta=1e-7)
        self.assertEqual(target.num_exp, topic.num_exposures)
        self.assertListEqual(target.exp_times, topic.exposure_times)

class MemoryTestClass(lsst.utils.tests.MemoryTestCase):
    pass

def setup_module(module):
    lsst.utils.tests.init()

if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
