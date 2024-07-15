# -*- coding: utf-8 -*-
"""
Created on Tue May  3 09:31:11 2022

@author: a179227
"""

from datetime import datetime, timezone
import math
import json
import cbor2
from observation import Observation
from esconstante import ES
from test_observation import obs_1, dat1, loc1, _res, prop1


def round_half(x):
    if x == 0:
        return 0
    sig = (x >= 0) * 2 - 1
    exp = min(max(round(math.log(abs(x), 2)), -14), 15)
    man = min(max(round(((abs(x) * 2**-exp) - 1) * 2**10), 0), 2**10)
    return sig * 2 ** (exp - 10) * (2**10 + man)


# %%% long
dic = {
    "type": "observation",
    "datation": [
        "2021-01-04T10:00:00",
        [["2021-01-05T08:00:00", "2021-01-05T12:00:00"]],
    ],
    "location": [
        [2.4123456, 48.9123456],
        [
            [
                [2.4123456, 48.9123456],
                [4.8123456, 45.8123456],
                [5.4123456, 43.3123456],
                [2.4123456, 48.9123456],
            ]
        ],
    ],
    "property": [{"prp": "PM10"}, {"prp": "Temp"}],
    "result": [51.348, {"low": 2.457}, 20.88, "high"],
    "idxref": {"datation": "location"},
}
len(json.dumps(dic))  # len : 388
len(
    cbor2.dumps(dic, datetime_as_timestamp=True, timezone=timezone.utc, canonical=True)
)  # len : 298

dic2 = {
    "d": [
        datetime(2021, 1, 4, 10),
        [[datetime(2021, 1, 5, 8), datetime(2021, 1, 5, 12)]],
    ],
    "l": [
        [round(2.4123456 * 10**7), round(48.9123456 * 10**7)],
        [
            [
                [round(2.4123456 * 10**7), round(48.9123456 * 10**7)],
                [round(4.8123456 * 10**7), round(45.8123456 * 10**7)],
                [round(5.4123456 * 10**7), round(43.3123456 * 10**7)],
                [round(2.4123456 * 10**7), round(48.9123456 * 10**7)],
            ]
        ],
    ],
    "p": [{"r": "PM10"}, {"r": "Temp"}],
    "s": [round_half(51.348), {"low": round_half(2.457)}, round_half(20.88), "high"],
    "x": {"d": "l"},
}
len(
    cbor2.dumps(dic2, datetime_as_timestamp=True, timezone=timezone.utc, canonical=True)
)  # len 132

dic2bis = {
    0: [
        datetime(2021, 1, 4, 10),
        [[datetime(2021, 1, 5, 8), datetime(2021, 1, 5, 12)]],
    ],
    1: [
        [round(2.4123456 * 10**7), round(48.9123456 * 10**7)],
        [
            [
                [round(2.4123456 * 10**7), round(48.9123456 * 10**7)],
                [round(4.8123456 * 10**7), round(45.8123456 * 10**7)],
                [round(5.4123456 * 10**7), round(43.3123456 * 10**7)],
                [round(2.4123456 * 10**7), round(48.9123456 * 10**7)],
            ]
        ],
    ],
    2: [{4: "PM10"}, {4: "Temp"}],
    3: [round_half(51.348), {"low": round_half(2.457)}, round_half(20.88), "high"],
    5: {0: 1},
}
len(
    cbor2.dumps(
        dic2bis, datetime_as_timestamp=True, timezone=timezone.utc, canonical=True
    )
)  # len 123

# %%% court
dic = {
    "type": "observation",
    "datation": "2021-01-04T10:00:00",
    "location": [2.4123456, 48.9123456],
    "property": {"prp": "PM10"},
    "result": 51.348,
}
len(json.dumps(dic))  # len : 142
len(
    cbor2.dumps(dic, datetime_as_timestamp=True, timezone=timezone.utc, canonical=True)
)  # len : 110
dic3 = {  # 1
    "d": datetime(2021, 1, 4, 10),  # 8  = 2 + 6
    "l": [round(2.4123456 * 10**7), round(48.9123456 * 10**7)],  # 13 = 2 + 1 + 5 + 5
    "p": {"r": "PM10"},  # 10 = 2 + 1 + 2 + 5
    "s": round_half(51.348),  # 5  = 2 + 3
}
len(
    cbor2.dumps(dic3, datetime_as_timestamp=True, timezone=timezone.utc, canonical=True)
)  # len 37

dic4 = {  # 1
    0: datetime(2021, 1, 4, 10),  # 7  = 1 + 6
    1: [round(2.4123456 * 10**7), round(48.9123456 * 10**7)],  # 12 = 1 + 1 + 5 + 5
    2: {4: "PM10"},  # 8  = 1 + 1 + 1 + 5
    3: round_half(51.348),  # 4  = 1 + 3
}
len(
    cbor2.dumps(dic4, datetime_as_timestamp=True, timezone=timezone.utc, canonical=True)
)  # len 32

# %%% interne
ob = Observation.obj(json.dumps(dict((obs_1, dat1, loc1, prop1, _res(1)))))
opt = {
    ES.dat_classES: ["value"],
    ES.loc_classES: ["value"],
    ES.prp_classES: ["valuemini"],
    ES.res_classES: ["sfloat"],
}
len(ob.to_bytes(opt))  # 24
