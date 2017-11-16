import unittest
import os

from lsst.ts.observatory.model import compare, read_conf_file
import lsst.utils.tests

class HelpersTest(unittest.TestCase):

    def test_read_conf_file(self):
        file_path = os.path.join(os.path.dirname(__file__), "dummy.conf")
        conf_dict = read_conf_file(file_path)
        self.assertEqual(len(conf_dict), 3)
        self.assertEqual(conf_dict["section1"]["par1"], 15.0)
        self.assertEqual(conf_dict["section1"]["par2"], "test")
        self.assertListEqual(conf_dict["section1"]["par3"],
                             ["good", "to", "go"])
        self.assertListEqual(conf_dict["section2"]["par4"],
                             [7.0, 8.0, 9.0])
        self.assertFalse(conf_dict["section2"]["par5"])
        self.assertEqual(conf_dict["section3"]["par6"], 0.5)
        self.assertListEqual(conf_dict["section3"]["par7"],
                             [("test1", 1.0, 30.0), ("test2", 4.0, 50.0)])

class MemoryTestClass(lsst.utils.tests.MemoryTestCase):
    pass

def setup_module(module):
    lsst.utils.tests.init()

if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
