# Analyse de l'intégrité du jeu de données IRVE
----------------
## Objectif
Le [jeu de données IRVE](https://doc.transport.data.gouv.fr/producteurs/infrastructures-de-recharge-de-vehicules-electriques-irve) est un jeu de données complexe avec un processus de production et de consolidation des données spécifique.     
Il fait l'objet également de questions concernant [l'intégrité des données](https://www.data.gouv.fr/fr/datasets/5448d3e0c751df01f85d0572/#/discussions). 
L'étude présentée ici a pour objectif de faciliter la réutilisation des données grace d'une part à une meilleure compréhension de la structure des données et d'autre part à une amélioration du niveau de qualité des données.

## Données IRVE
Les données IRVE sont décrites dans le [schéma de données](https://schema.data.gouv.fr/etalab/schema-irve-statique/2.2.0/documentation.html) mis à disposition. Celui-ci décrit chacun des champs qui le compose.    
Par contre, il ne décrit pas la structure globale des données qui permet de comprendre les relations qui existent entre chaque champs. Le modèle de données ci-dessous identifie les principales entités que décrivent les champs et les relations entre celles-ci :

*Notation:*
- *M : Mandatory - documentation obligatoire*
- *PK : Primary Key - identifiant unique de l'entité*
- *Root : champ fictif associé à une ligne du tableau*
```mermaid
erDiagram
    AMENAGEUR ||..|{ STATION : amenage
    AMENAGEUR {
        string nom_amenageur
        string siren_amenageur
        string contact_amenageur 
    }
    OPERATEUR ||..|{ STATION : "exploite pour le compte de l enseigne"
    OPERATEUR {
        string contact_operateur PK "M"
        string nom_operateur 
        string telephone_operateur 
    }
    ENSEIGNE ||..|{ STATION : "heberge"
    ENSEIGNE {
        string nom_enseigne PK "M" 
    }
    STATION {
        string  id_station_itinerance PK "M"
        string  nom_station "M"
        enum    implantation_station "M"
        integer nbre_pdc "M"
        string  condition_acces "M"
        string  horaires "M"
        boolean station_deux_roues "M"
        string  id_station_local
        enum    raccordement
        string  num_pdl
        date    date_mise_en_service 
    }
    LOCALISATION ||--|{ STATION : "localise"
    LOCALISATION {
       array   coordonneesXY PK "M"
       string  adresse_station "M"
       string  code_insee_commune 
    }
    STATION ||--|{ POINT_DE_CHARGE : regroupe
    POINT_DE_CHARGE {
        string id_pdc_itinerance PK "M Root"
        number puissance_nominale "M"
        boolean prise_type_ef "M"
        boolean prise_type_2 "M"
        boolean prise_type_combo_ccs "M"
        boolean prise_type_chademo "M"
        boolean prise_type_autre "M"
        boolean paiement_acte "M"
        boolean paiement_autre "M"
        boolean reservation "M"
        enum    accessibilite_pmr "M"
        string  restriction_gabarit "M"
        date    date_maj "M"
        string  id_pdc_local
        boolean gratuit
        boolean paiement_cb
        string  tarification
        string  observations
        boolean cable_t2_attache 
    }
```
