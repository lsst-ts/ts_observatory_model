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

import collections
import math
import unittest

from lsst.ts.observatory.model import Target


class TargetTest(unittest.TestCase):
    def setUp(self):
        self.targetId = 3
        self.fieldId = 2573
        self.band_filter = "r"
        self.ra = 300.518929
        self.dec = -1.720965
        self.ang = 45.0
        self.num_exposures = 2
        self.exposure_times = [15.0, 15.0]

        self.alt = 45.0
        self.az = 225.0
        self.rot = 30.0
        self.telalt = 45.0
        self.telaz = 225.0
        self.telrot = 30.0

        self.ra_rad = math.radians(self.ra)
        self.dec_rad = math.radians(self.dec)
        self.ang_rad = math.radians(self.ang)
        self.alt_rad = math.radians(self.alt)
        self.az_rad = math.radians(self.az)
        self.rot_rad = math.radians(self.rot)
        self.telalt_rad = math.radians(self.telalt)
        self.telaz_rad = math.radians(self.telaz)
        self.telrot_rad = math.radians(self.telrot)

        self.target = Target(
            self.targetId,
            self.fieldId,
            self.band_filter,
            self.ra_rad,
            self.dec_rad,
            self.ang_rad,
            self.num_exposures,
            self.exposure_times,
        )
        self.target.alt_rad = self.alt_rad
        self.target.az_rad = self.az_rad
        self.target.rot_rad = self.rot_rad
        self.target.telalt_rad = self.telalt_rad
        self.target.telaz_rad = self.telaz_rad
        self.target.telrot_rad = self.telrot_rad

    def test_basic_information_after_creation(self):
        self.assertEqual(self.target.targetid, self.targetId)
        self.assertEqual(self.target.fieldid, self.fieldId)
        self.assertEqual(self.target.filter, self.band_filter)
        self.assertEqual(self.target.ra, self.ra)
        self.assertEqual(self.target.dec, self.dec)
        self.assertEqual(self.target.num_exp, self.num_exposures)
        self.assertListEqual(self.target.exp_times, self.exposure_times)

    def test_json_serialization(self):
        jsondump = self.target.to_json()
        target2 = Target()
        target2.from_json(jsondump)
        self.assertEqual(self.target.targetid, target2.targetid)
        self.assertEqual(self.target.fieldid, target2.fieldid)
        self.assertEqual(self.target.filter, target2.filter)
        self.assertEqual(self.target.ra_rad, target2.ra_rad)
        self.assertEqual(self.target.dec_rad, target2.dec_rad)
        self.assertEqual(self.target.num_exp, target2.num_exp)
        self.assertListEqual(self.target.exp_times, target2.exp_times)

    def test_json_ingest_has_required_params(self):
        self.assertRaises(KeyError, self.init_target_with_bad_json)

    def init_target_with_bad_json(self):

        missingfilter = (
            '{"targetid": 3, "fieldid": 2573, "ra_rad": 5.24504477561707, '
            '"dec_rad": -0.030036505561584215, "ang_rad": 0.7853981633974483, '
            '"num_exp": 2, "exp_times": [15.0, 15.0], "_exp_time": null, '
            '"time": 0.0, "airmass": 0.0, "sky_brightness": 0.0, "cloud": 0.0, '
            '"seeing": 0.0, "propid": 0, "need": 0.0, "bonus": 0.0, "value": 0.0, '
            '"goal": 0, "visits": 0, "progress": 0.0, '
            '"sequenceid": 0, "subsequencename": "", "groupid": 0, "groupix": 0, '
            '"is_deep_drilling": false, "is_dd_firstvisit": false, "remaining_dd_visits": 0, '
            '"dd_exposures": 0, "dd_filterchanges": 0, "dd_exptime": 0.0, '
            '"alt_rad": 0.7853981633974483, "az_rad": 3.9269908169872414, '
            '"rot_rad": 0.5235987755982988, "telalt_rad": 0.7853981633974483, '
            '"telaz_rad": 3.9269908169872414, "telrot_rad": 0.5235987755982988, "propboost": 1.0, '
            '"slewtime": 0.0, "cost": 0.0, "rank": 0.0, "num_props": 0, "propid_list": [], '
            '"need_list": [], "bonus_list": [], "value_list": [], "propboost_list": [], '
            '"sequenceid_list": [], "subsequencename_list": [], "groupid_list": [], '
            '"groupix_list": [], "is_deep_drilling_list": [], '
            '"is_dd_firstvisit_list": [], "remaining_dd_visits_list": [], '
            '"dd_exposures_list": [], "dd_filterchanges_list": [], "dd_exptime_list": [], '
            '"last_visit_time": 0.0, "note": ""}'
        )
        t = Target()
        t.from_json(missingfilter)

    def test_string_representation(self):
        truth_str = (
            "targetid=3 field=2573 filter=r exp_times=[15.0, 15.0] "
            "ra=300.519 dec=-1.721 ang=45.000 alt=45.000 az=225.000 "
            "rot=30.000 telalt=45.000 telaz=225.000 telrot=30.000 "
            "time=0.0 airmass=0.000 brightness=0.000 "
            "cloud=0.00 seeing=0.00 visits=0 progress=0.00% "
            "seqid=0 ssname= groupid=0 groupix=0 "
            "firstdd=False ddvisits=0 "
            "need=0.000 bonus=0.000 value=0.000 propboost=1.000 "
            "propid=[] need=[] bonus=[] value=[] propboost=[] "
            "slewtime=0.000 cost=0.000 rank=0.000 note="
        )
        self.assertEqual(str(self.target), truth_str)

    def test_driver_state_copy(self):
        target2 = Target()
        target2.copy_driver_state(self.target)
        self.assertEqual(target2.alt_rad, self.alt_rad)
        self.assertEqual(target2.az_rad, self.az_rad)
        self.assertEqual(target2.ang_rad, self.ang_rad)
        self.assertEqual(target2.rot_rad, self.rot_rad)
        self.assertEqual(target2.telalt_rad, self.telalt_rad)
        self.assertEqual(target2.telaz_rad, self.telaz_rad)
        self.assertEqual(target2.telrot_rad, self.telrot_rad)

    def test_copy_creation(self):
        target2 = self.target.get_copy()
        target2.targetid = 10
        target2.fieldid = 2142
        self.assertEqual(self.target.targetid, self.targetId)
        self.assertEqual(target2.targetid, 10)
        self.assertEqual(self.target.fieldid, self.fieldId)
        self.assertEqual(target2.fieldid, 2142)

    def test_creation_from_topic(self):
        topic = collections.namedtuple(
            "topic",
            [
                "targetId",
                "fieldId",
                "filter",
                "ra",
                "decl",
                "skyAngle",
                "numExposures",
                "exposureTimes",
            ],
        )
        topic.targetId = 1
        topic.fieldId = -1
        topic.filter = "z"
        topic.ra = 274.279376
        topic.decl = -14.441534
        topic.skyAngle = 45.0
        topic.numExposures = 3
        topic.exposureTimes = [5.0, 10.0, 5.0]
        target = Target.from_topic(topic)
        self.assertEqual(target.targetid, topic.targetId)
        self.assertEqual(target.fieldid, topic.fieldId)
        self.assertEqual(target.filter, topic.filter)
        self.assertEqual(target.ra, topic.ra)
        self.assertAlmostEqual(target.dec, topic.decl, delta=1e-7)
        self.assertEqual(target.num_exp, topic.numExposures)
        self.assertListEqual(target.exp_times, topic.exposureTimes)


if __name__ == "__main__":
    unittest.main()
