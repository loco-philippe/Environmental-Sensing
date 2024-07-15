# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: Philippe@loco-labs.io

The `observation.test_mongo` module contains the tests (class unittest) for the
`observation.essearch` methods.
The dataset used is defined in `observation.Tests.data.py`
"""

import unittest
from datetime import datetime
import requests as rq
from pymongo import MongoClient
from observation.essearch import ESSearch

# Requires the PyMongo package# https://api.mongodb.com/python/current
# pathClient = 'mongodb+srv://ESobsUser:observation@esobs.gwpay.mongodb.net/test'


def clientMongo(
    user="ESobsUser", pwd="observation", site="esobs.gwpay.mongodb.net/test"
):
    auth = "authSource=admin"
    replicaSet = "replicaSet=atlas-13vws6-shard-0"
    readPref = "readPreference=primary"
    appName = "appname=MongoDB%20Compass"
    ssl = "ssl=true"
    st = (
        "mongodb+srv://"
        + user
        + ":"
        + pwd
        + "@"
        + site
        + "?"
        + auth
        + "&"
        + replicaSet
        + "&"
        + readPref
        + "&"
        + appName
        + "&"
        + ssl
    )
    return MongoClient(st)


def envoi_mongo_url(data):
    url = "https://webhooks.mongodb-realm.com/api/client/v2.0/app/observation_app-wsjge/service/postObs/incoming_webhook/api?secret=10minutes"
    r = rq.post(url, data=data)
    print("réponse : ", r.text, "\n")
    return r.status_code


def envoi_mongo_python(data):
    user = "ESobsUser"
    pwd = "observation"
    site = "esobs.gwpay.mongodb.net/test"

    st = (
        "mongodb+srv://"
        + user
        + ":"
        + pwd
        + "@"
        + site
        + "?"
        + "authSource=admin"
        + "&"
        + "replicaSet=atlas-13vws6-shard-0"
        + "&"
        + "readPreference=primary"
        + "&"
        + "appname=MongoDB%20Compass"
        + "&"
        + "ssl=true"
    )
    client = MongoClient(st)

    baseMongo = "test_obs"
    collection = "observation"
    collec = client[baseMongo][collection]
    return collec.insert_one(data).inserted_id
    # try : return collec.insert_one(data).inserted_id
    # except : return None


client = clientMongo()

from data import obs_mixte, obs_tests

ob_mixte = obs_mixte()
ob_tests = obs_tests()

ob_mesure = ob_tests[:30]
ob_signal = ob_tests[30:40]
ob_fixe = ob_tests[40:42]
ob_mob_1 = ob_tests[42:44]
ob_mobile = ob_tests[44:46]
ob_multi = ob_tests[46:48]
ob_dalle = ob_tests[48:50]
ob_m_dal = ob_tests[50:52]
ob_liste = [
    ob_mesure,
    ob_signal,
    ob_fixe,
    ob_mob_1,
    ob_mobile,
    ob_multi,
    ob_dalle,
    ob_m_dal,
]
type0 = [ob[0].param["type"] for ob in ob_liste]
name0 = [ob[0].name for ob in ob_liste]
len_ob = [len(ob) for ob in ob_liste]


class Test_jeu_data_py(unittest.TestCase):
    collec = client["test_search"]["jeu_data_py3"]

    def test_param_name(self):
        srch = ESSearch(Test_jeu_data_py.collec)
        for typ, nam, leno, lis in zip(type0, name0, len_ob, ob_liste):
            srch.addCondition(path="_metadata.param.type", operand=typ, comparator="==")
            result = srch.execute("idfused")
            # print(len(result))
            self.assertTrue(len(result) == leno and result == lis)
            srch.clearConditions()
        srch.addCondition(path="_metadata.name", comparator="regex", operand="mesures")
        result = srch.execute("idfused")
        self.assertTrue(result == ob_tests[40:52])
        srch.addCondition(path="_metadata.name", comparator="regex", operand="polluant")
        result = srch.execute("idfused")
        self.assertTrue(result == ob_tests[40:48] + ob_tests[50:52])

    def test_datation(self):
        srch = ESSearch(Test_jeu_data_py.collec)
        srch.addCondition(
            "datation", comparator=">=", operand=datetime(2022, 1, 2, 0, 0)
        )
        srch.addCondition(
            "datation", comparator="<=", operand=datetime(2022, 1, 4, 0, 0)
        )

        srch.addCondition(path="_metadata.name", comparator="regex", operand="mobile")
        result = srch.execute("idfused")
        self.assertTrue(len(result) == 1)
        self.assertTrue(ob_tests[42].loc(result[0][0], row=True) == [1])
        self.assertTrue(ob_tests[42].loc(result[0][1], row=True) == [2])
        self.assertTrue(result[0].idxlen == [2, 2, 2, 2, 2, 1, 1, 1])


class Test_ntv_py(unittest.TestCase):
    def test_insert(self):
        client = clientMongo()
        collec = client["NTV"]["test"]

        ntv = Ntv.obj(
            {
                "ntv": "essai1",
                "test": {
                    "date": datetime.datetime(2010, 2, 10),
                    "coord:point": [42.1, 3.2],
                },
            }
        )
        collec.insert_one(ntv.to_obj(format="cbor"))
        js = collec.find_one({"ntv": "essai1"})
        collec.delete_one({"_id": js["_id"]})
        js.pop("_id")
        self.assertEqual(Ntv.obj(js), ntv)


if __name__ == "__main__":
    unittest.main(verbosity=2)
