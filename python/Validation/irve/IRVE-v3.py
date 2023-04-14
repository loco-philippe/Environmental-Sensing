#!/usr/bin/env python
# coding: utf-8

# # Objet : Analyse des relations entre champs des données IRVE
# 
# ## Contexte
# - clarification du rôle des modèles de données dans les jeux de données (cf mise à jour récente des [guides data.gouv](https://guides.etalab.gouv.fr/qualite/documenter-les-donnees/))
# - intégration d'une propriété "relationship" dans les schémas de données ([issue TableSchema](https://github.com/frictionlessdata/specs/issues/803) en cours de validation)
# - création d'outils de contrôle des relations entre champs des jeux de données tabulaires (cf usage ci-dessous)
# 
# ## Objectifs
# - valider sur un cas réel l'utilisation d'un modèle de données en complément d'un schéma de données
# - identifier les apports que pourraient avoir les contrôles de validation des relations entre champs
# 
# ## Résultats
# - la formalisation d'un modèle de données facilite la compréhension des données et des relations entre champs
# - l'outil de contrôle permet d'améliorer significativement la qualité des données par la détection d'incohérences de relations
# - l'analyse a posteriori permet de (re)trouver la logique de dépendance entre les colonnes qui minimise les incohérences
# - les incohérences détectées sur le jeu de données IRVE restent faibles (inférieures à 2% des point de charge documentés - voir chapitre 4)
# 
# ## Suite à donner
# - Mettre à jour, valider et publier le modèle de données IRVE
# - Définir les contrôles supplémentaires à intégrer pour toutes nouvelles données ainsi que pour le jeu complet
# - Mettre en oeuvre les outils de contrôle
# 
# ## Evolutions possibles 
# - Ajouter dans les guides d'Etalab un guide pour les modèles de données 
# - Intégrer dans les schémas de données la propriété "relationship" en cours de validation,
# - Définir un indicateur qui mesure l'écart (existant / attendu) des relations entre champs
# 
# données utilisées : https://www.data.gouv.fr/fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques/    
# fichier : "*consolidation-etalab-schema-irve-statique-v-2.2.0-20230303.csv*"


from datetime import datetime
import json
from observation import Ilist, Analysis
import pandas as pd

def analyse_integrite(data, fields):
    '''analyse les relations du DataFrame définies dans le dict fields et retourne un dict avec pour chaque contrôle la
    liste des index ko. Les résultats des contrôles sont également ajoutés sous forme de champs booléens à data'''
    analyse = Analysis(data)
    dic_res = analyse.check_relationship(fields)
    data['ok'] = True
    for name, lis in dic_res.items():
        data[name] = True
        data.loc[lis, name] = False
        data['ok'] = data['ok'] & data[name]
        #print('{:<50} {:>5}'.format(name, len(data) - data[name].sum()))
    return dic_res

log = {'date_irve': '2023-03-03', 'file': 'consolidation-etalab-schema-irve-statique-v-2.2.0-20230303.csv',
      'chemin': 'https://raw.githubusercontent.com/loco-philippe/Environmental-Sensing/main/python/Validation/irve/'}
irve = pd.read_csv(log['chemin'] + log['file'], sep=',', low_memory=False)
log['len_irve'] = len(irve)
print('nombre de lignes : ', log['len_irve']) 


# ## schéma de données
# Le schéma de données restreint à la propriété 'relationship' et construit à partir du modèle de données est le suivants :

# In[142]:


fields = [
 
 # relation unicité des pdl
 { "name": "index",
   "relationship" : { "parent" : "id_pdc_itinerance", "link" : "coupled" }},   
 # relations inter entités
 { "name": "contact_operateur",
   "relationship" : { "parent" : "id_station_itinerance", "link" : "derived" }},
 { "name": "nom_enseigne",
   "relationship" : { "parent" : "id_station_itinerance", "link" : "derived" }},
 { "name": "coordonneesXY",
   "relationship" : { "parent" : "id_station_itinerance", "link" : "derived" }},
 { "name": "id_station_itinerance",
   "relationship" : { "parent" : "id_pdc_itinerance",     "link" : "derived" }},
 # relations intra entité - station
 { "name": "nom_station",
   "relationship" : { "parent" : "id_station_itinerance", "link" : "derived" }},
 { "name": "implantation_station",
   "relationship" : { "parent" : "id_station_itinerance", "link" : "derived" }},
 { "name": "nbre_pdc",
   "relationship" : { "parent" : "id_station_itinerance", "link" : "derived" }},
 { "name": "condition_acces",
   "relationship" : { "parent" : "id_station_itinerance", "link" : "derived" }},
 { "name": "horaires",
   "relationship" : { "parent" : "id_station_itinerance", "link" : "derived" }},
 { "name": "station_deux_roues",
   "relationship" : { "parent" : "id_station_itinerance", "link" : "derived" }},
 # relations intra entité - localisation
 { "name": "adresse_station",
   "relationship" : { "parent" : "coordonneesXY",         "link" : "derived" }} ]


# In[143]:


relations = ['index', 'contact_operateur', 'nom_enseigne', 'coordonneesXY', 'adresse_station', 'id_station_itinerance', 
             'nom_station', 'implantation_station', 'nbre_pdc', 'condition_acces', 'horaires', 'station_deux_roues', 
             'id_pdc_itinerance', 'date_maj', 'last_modified']
champs =  ['contact_operateur', 'nom_enseigne', 'coordonneesXY', 'adresse_station', 'id_station_itinerance', 'nom_station',
           'implantation_station', 'nbre_pdc', 'condition_acces', 'horaires', 'station_deux_roues', 'id_pdc_itinerance', 
           'puissance_nominale', 'prise_type_ef', 'prise_type_2', 'prise_type_combo_ccs', 'prise_type_chademo', 
           'prise_type_autre', 'paiement_acte', 'paiement_autre', 'reservation',  'accessibilite_pmr', 'restriction_gabarit', 
           'date_maj', 'last_modified']


# -----------------------
# ## 3 - Séparation des pdc itinerance et hors itinerance
# - un peu moins de 1 % des points de charge sont hors itinerance

data = irve
data[['id_station_itinerance','id_pdc_itinerance']] = data[['id_station_itinerance','id_pdc_itinerance']].astype('string')
#data[['last_modified','date_maj']] = data[['last_modified','date_maj']].astype('datetime64')
data['non_concerne'] = data['id_station_itinerance'].str.contains('oncern') | data['id_pdc_itinerance'].str.contains('oncern')

non_concerne = data[data['non_concerne']].reset_index()['index']
itinerance = data[~data['non_concerne']].reset_index()
itinerance_init = itinerance.loc[:, relations]
log['pdc_hors_itinerance'] = len(non_concerne)
log['pdc_en_itinerance'] = len(itinerance)
print('nombre de pdc hors itinerance : ', log['pdc_hors_itinerance'])
print('nombre de pdc en itinerance   : ', log['pdc_en_itinerance'])


# -----------------------
# ## 4 - Bilan initial intégrité
# - 36 % des lignes sont erronées ( 18 116 )

# In[147]:


# séparation données bonnes (itinerance_ok_1) et données résiduelles (itinerance_1)
res = analyse_integrite(itinerance_init, fields)
itinerance_ok_1 = itinerance_init.loc[itinerance_init.ok, relations].reset_index(drop=True)
itinerance_1 = itinerance_init.loc[~itinerance_init.ok, relations].reset_index(drop=True)
itinerance_init = itinerance_init.loc[:, relations]
log['init_ok'] = len(itinerance_ok_1)
log['init_ko'] = len(itinerance_1)
print("\nnombre d'enregistrements sans erreurs : ", log['init_ok'])
print("nombre d'enregistrements avec au moins une erreur : ", log['init_ko'])
print("taux d'erreur : ", round(log['init_ko'] / log['pdc_en_itinerance'] * 100), ' %')


# -----------------------
# ## 5 - Séparation doublons pdc - date de maj
# - la moitié des pdc en erreur sont liées aux doublons de pdc
# - la suppression des doublons permet de diviser par 5 le nombre de lignes erronnées ( 2 166 )

# In[148]:


# séparation doublons pdc (doublons_pdc) et données résiduelles (itinerance_2)
itinerance_1['doublons_pdc'] = itinerance_1.sort_values(by='date_maj').duplicated('id_pdc_itinerance', keep='last')

doublons_pdc = itinerance_1[itinerance_1['doublons_pdc']].loc[:, relations].reset_index(drop=True)['index']
itinerance_2 = itinerance_1[~itinerance_1['doublons_pdc']].loc[:, relations].reset_index(drop=True)
itinerance_1 = itinerance_1.loc[:, relations]
log['doublons_pdc'] = len(doublons_pdc)
log['sans_doublons_pdc'] = len(itinerance_2)
print('nombre de doublons pdc : ', log['doublons_pdc'])
print('nombre de pdc sans doublon   : ', log['sans_doublons_pdc'])


# In[149]:


# séparation données bonnes (itinerance_ok_3) et données résiduelles (itinerance_3)
res = analyse_integrite(itinerance_2, fields)
itinerance_ok_3 = itinerance_2.loc[itinerance_2.ok, relations].reset_index(drop=True)
itinerance_3 = itinerance_2.loc[~itinerance_2.ok, relations].reset_index(drop=True)
itinerance_2 = itinerance_2.loc[:, relations]
log['etape3_ok'] = len(itinerance_ok_3)
log['etape3_ko'] = len(itinerance_3)
print("\nnombre d'enregistrements sans erreurs : ", log['etape3_ok'])
print("nombre d'enregistrements avec au moins une erreur : ", log['etape3_ko'])


# -----------------------
# ## 6 - Séparation doublons station - date de maj
# - 20% des erreurs résiduelles sont liées au mélange d'anciens et de nouveaux pdc
# - la suppression des anciens pdc permet de réduire de 25% le nombre de lignes erronnées ( 1 616 )
# - les dernières erreurs correspondent à 468 stations associées à 32 opérateurs et sont liées à des causes multiples

# In[150]:


# séparation doublons stations (doublons_stat_maj) et données résiduelles (itinerance_4)
itinerance_3['stat_maj'] = itinerance_3.id_station_itinerance + itinerance_3.date_maj
stat_maj_unique = itinerance_3.sort_values(by='stat_maj').drop_duplicates('id_station_itinerance', keep='last')
itinerance_3['last_stat_maj'] = itinerance_3['stat_maj'].isin(stat_maj_unique['stat_maj'])

doublons_stat_maj = itinerance_3[~itinerance_3['last_stat_maj']].loc[:, relations].reset_index(drop=True)['index']
itinerance_4 = itinerance_3[itinerance_3['last_stat_maj']].loc[:, relations].reset_index(drop=True)
itinerance_3 = itinerance_3.loc[:, relations]
log['doublons_station'] = len(doublons_stat_maj)
log['sans_doublons_station'] = len(itinerance_4)
print('nombre de doublons stations : ', log['doublons_station'])
print('nombre de pdc sans doublon   : ', log['sans_doublons_station'])


# In[151]:


# séparation données bonnes (itinerance_ok_5) et données résiduelles (itinerance_5 / itinerance_5_full)
res = analyse_integrite(itinerance_4, fields)
itinerance_ok_5 = itinerance_4.loc[itinerance_4.ok, relations].reset_index(drop=True)
itinerance_5_full = itinerance_4.loc[~itinerance_4.ok].reset_index(drop=True)
itinerance_5 = itinerance_5_full.loc[:, relations]
#itinerance_4 = itinerance_4.loc[:, relations]
log['etape5_ok'] = len(itinerance_ok_5)
log['etape5_ko'] = len(itinerance_5)
print("\nnombre d'enregistrements sans erreurs : ", log['etape5_ok'])
print("nombre d'enregistrements avec au moins une erreur : ", log['etape5_ko'])



# -----------------------
# ## 7 - Synthèse
# 

# In[154]:


# consolidation des données
itinerance['doublons_stat_maj'] = itinerance['index'].isin(doublons_stat_maj)
itinerance['doublons_pdc'] = itinerance['index'].isin(doublons_pdc)
itinerance['lignes_a_corriger'] = itinerance['index'].isin(itinerance_5['index'])
itinerance['doublons_a_supprimer'] = itinerance['doublons_stat_maj'] | itinerance['doublons_pdc']
itinerance['lignes_ko'] = itinerance['doublons_a_supprimer'] | itinerance['lignes_a_corriger']
print('total des lignes à corriger : ', itinerance['lignes_a_corriger'].sum())
itinerance_doublons = itinerance[itinerance['doublons_a_supprimer']].reset_index(drop=True)
print('total des doublons à supprimer : ', len(itinerance_doublons))
itinerance_ok = itinerance[~itinerance['lignes_ko']].reset_index(drop=True)
print('nombre de pdc avec controles ok : ', len(itinerance_ok))


# In[155]:


#fichier csv des lignes résiduelles à traiter (IRVE_residuel)
#fichier csv des données itinerance avec indicateur des données à corriger ou à ignorer (IRVE_itinerance_complet)
#fichier csv des données itinerance valides (IRVE_itinerance_valide)
#fichier csv des doublons (IRVE_itinerance_doublons)
extension = log['date_irve'] +'.csv'
itinerance_5_full.to_csv('IRVE_residuel' + extension)
itinerance.to_csv('IRVE_itinerance_complet' + extension)
itinerance_ok.to_csv('IRVE_itinerance_valide' + extension)
itinerance_doublons.to_csv('IRVE_itinerance_doublons' + extension)
log['IRVE_residuel' + extension] = len(itinerance_5_full)
log['IRVE_itinerance_complet' + extension] = len(itinerance)
log['IRVE_itinerance_valide' + extension] = len(itinerance_ok)
log['IRVE_itinerance_doublons' + extension] = len(itinerance_doublons)


# In[156]:


# vérification de l'intégrité
print('\nbilan intégrité :')
res = analyse_integrite(itinerance_ok.loc[:, relations], fields)
log['bilan_erreurs'] = sum([len(controle) for controle in res.values()])
log['date'] = datetime.now().isoformat()
print('\nerreurs : ', log['bilan_erreurs'])


# In[157]:


with open('logfile.txt', 'a', encoding="utf-8") as f:
    f.write(json.dumps(log) + '\n')
print(log)

