# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 10:49:19 2022

@author: philippe@loco-labs.io

objet : tests opendata sur la base adresse nationale
points identifiés :
    - lecture fichiers csv et json -> même résultat
    - mise en évidence du typage des données non défini en csv
    - mise en évidence du format json non explicite (champs json non définis)
    - nécessité de retraitement pour reconstruire les données
    - gain de taille significatif sur le stockage ( 18% sur csv, 76% sur json, 89% sur xls)
    - identification des colonnes et lignes de référence
    - indicateurs sur les données
"""

import os
import math

os.chdir(
    "C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/ES"
)
from ilist import Ilist
from pprint import pprint

chemin = "C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/validation/cours/"
file = chemin + "example cours.csv"
filebin = chemin + "example cours.il"

# %% student
annew2020 = Ilist.Iedic(
    {"notes": [14, 12, 13, 15, 17]},
    {
        "course": ["english", "english", "math", "math", "math"],
        "examen": ["t3", "t4", "t1", "t2", "t3"],
    },
)
annew2021 = Ilist.Iedic(
    {"notes": [10, 12, 11, 13, 15]},
    {
        "course": ["english", "english", "math", "math", "math"],
        "examen": ["t2", "t3", "t1", "t2", "t4"],
    },
)
camir2020 = Ilist.Iedic(
    {"notes": [19, 20, 6, 4]},
    {
        "course": ["software", "software", "spanish", "spanish"],
        "examen": ["t2", "t3", "t1", "t4"],
    },
)
camir2021 = Ilist.Iedic(
    {"notes": [17, 18, 2, 4]},
    {
        "course": ["software", "software", "spanish", "spanish"],
        "examen": ["t3", "t4", "t1", "t2"],
    },
)
judig2020 = Ilist.Iedic(
    {"notes": [7, 12, 14, 12]},
    {
        "course": ["software", "software", "software", "spanish"],
        "examen": ["t1", "t2", "t3", "t4"],
    },
)
judig2021 = Ilist.Iedic(
    {"notes": [5, 10, 12, 10]},
    {
        "course": ["software", "software", "software", "spanish"],
        "examen": ["t1", "t3", "t4", "t2"],
    },
)
philb2020 = Ilist.Iedic(
    {"notes": [8, 20]}, {"course": ["english", "math"], "examen": ["t3", "t2"]}
)
philb2021 = Ilist.Iedic(
    {"notes": [18, 6]}, {"course": ["software", "english"], "examen": ["t3", "t4"]}
)
philw2020 = Ilist.Iedic(
    {"notes": [10, 17]}, {"course": ["history", "math"], "examen": ["t2", "t1"]}
)
philw2021 = Ilist.Iedic(
    {"notes": [8, 15]}, {"course": ["history", "math"], "examen": ["t2", "t1"]}
)
# %% group
group2020 = Ilist.Iedic(
    {"notes": [annew2020, camir2020, judig2020, philb2020, philw2020]},
    {
        "full name": [
            "anne white",
            "camille red",
            "judith grey",
            "philippe black",
            "philippe white",
        ],
        "last name": ["white", "red", "grey", "black", "white"],
        "first name": ["anne", "camille", "judith", "philippe", "philippe"],
        "surname": ["skyler", "saul", "marie", "gus", "heisenberg"],
        "group": ["gr2", "gr3", "gr3", "gr1", "gr2"],
    },
)
group2021 = Ilist.Iedic(
    {"notes": [annew2021, camir2021, judig2021, philb2021, philw2021]},
    {
        "full name": [
            "anne white",
            "camille red",
            "judith grey",
            "philippe black",
            "philippe white",
        ],
        "last name": ["white", "red", "grey", "black", "white"],
        "first name": ["anne", "camille", "judith", "philippe", "philippe"],
        "surname": ["skyler", "saul", "marie", "gus", "heisenberg"],
        "group": ["gr1", "gr3", "gr3", "gr1", "gr2"],
    },
)

# %% global
abq = Ilist.Iedic(
    {"notes": [group2020, group2021]},
    {"year": [2020, 2021], "school": ["albuquerque", "albuquerque"]},
)
abqm = abq.merge()  # len : 34
print(
    "taille json (raw / merged) : ",
    len(abq.json(encoded=True)),
    len(abqm.json(encoded=True)),
)  # 2618 1637
print(
    "taille cbor (raw / merged) : ",
    len(abq.json(encoded=True, encode_format="cbor")),
    len(abqm.json(encoded=True, encode_format="cbor")),
)  # 1597 760
print("taille fichier csv: ", abqm.to_csv(file))  # 2903

# %% analyse fichier CSV
l = ["str" for i in range(10)]
l[8] = l[9] = "int"
il = Ilist.from_csv(file, valfirst=False, header=True, dtype=l, delimiter=",")
print("taille fichier json : ", il.to_file(filebin, encode_format="json"))  # 1637
print("taille fichier cbor: ", il.to_file(filebin, encode_format="cbor"), "\n")  # 760
pprint(il._dict())

il.couplingmatrix(chemin + "matrice.txt")
print("\n", "longueur full (5 index) : ", il.lencompletefull)  # 600

print(
    "axes coupling (1: coupled, 0 : not) - descending : ", il.axescoupling(il.axesmin)
)
il.mergeidx([0, 3, 4])
print("taille index, longueur full dim 3 opt : ", il.idxlen, il.lencompletefull)  # 104
il.swapindex([0, 1, 2, 3, 4, 5, 6, 7, 8])

il.mergeidx([3, 4])
il.mergeidx([0, 1])
print(" longueur full dim 3 : ", il.lencompletefull, "\n")  # 180
il.swapindex([0, 1, 2, 3, 4, 5, 6, 7, 8])

il.mergeidx([0, 1, 3, 4])
print(" longueur full dim 2 : ", il.lencompletefull)  # 56
pprint(il._dict())
il.swapindex([0, 1, 2, 3, 4, 5, 6, 7, 8])

il.mergeidx([0, 1, 3, 4, 8])
print(" longueur full dim 1 : ", il.lencompletefull)  # 34
il.swapindex([0, 1, 2, 3, 4, 5, 6, 7, 8])

il.mergeidx([3, 4])
print(" longueur full dim 4 : ", il.lencompletefull)  # 240
il.swapindex([0, 1, 2, 3, 4, 5, 6, 7, 8])

# %% xarray
print(il.to_xarray(fillvalue=math.nan))
print(il.to_xarray(dimmax=4, fillvalue=math.nan))
print(il.to_xarray(dimmax=3, fillvalue=math.nan))
print(il.to_xarray(dimmax=2, fillvalue=math.nan))

# %% cours light

filelight = chemin + "example cours light.csv"
l = ["str" for i in range(9)]
l[6] = l[8] = "int"
il = Ilist.from_csv(filelight, delimiter=";", dtype=l)
print(il.to_xarray(fillvalue=math.nan))
print(il.to_xarray(dimmax=2, fillvalue=math.nan))
