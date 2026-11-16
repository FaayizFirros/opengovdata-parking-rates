import unittest
from scripts.sync_ura_parking import normalise, generate

class ParkingRateTest(unittest.TestCase):
    def test_official_car_rate(self):
        r=normalise({"ppCode":"A0004","ppName":"ALIWAL STREET","vehCat":"Car",
                     "weekdayRate":"$0.50","weekdayMin":"30mins","startTime":"08.30 AM"})
        self.assertEqual("A0004",r["code"])
        self.assertEqual("30mins",r["weekday_min"])
    def test_non_car_not_published(self):
        self.assertIsNone(normalise({"ppCode":"A0004","vehCat":"Motorcycle","weekdayRate":"$0.50"}))
    def test_no_secret_in_export(self):
        def fake(url,headers):
            if "insertNewToken" in url:
                return {"Status":"Success","Result":"secret-token-here"}
            return {"Status":"Success","Result":[{"ppCode":"A0004","vehCat":"Car",
                                                  "weekdayRate":"$0.50"}]}
        d=generate("a-private-key",request=fake)
        self.assertNotIn("secret-token",str(d))
        self.assertNotIn("a-private-key",str(d))
    def test_fail_closed_when_dataset_empty(self):
        def fake(url,headers):
            if "insertNewToken" in url:
                return {"Status":"Success","Result":"secret-token-here"}
            return {"Status":"Success","Result":[]}
        with self.assertRaises(RuntimeError):
            generate("secret",request=fake)
