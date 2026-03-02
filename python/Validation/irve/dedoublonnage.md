# Dédoublonnage

Les doublons concernent les points de recharge et les stations.

## Identification des entités

Les entités stations et points de recharge sont identifiés par leur Id (id_pdc_itinerance et id_station_itinerance).

Dans le cas du fichier consolidé IRVE, on peut intègrer des données de plusieurs origines et avec également un historique :

- date de mise à jour (date_maj) : ceci permet de distinguer deux versions d'une même entité
- origine (datagouv_organization_or_owner): ceci permet d'identifier deux entités produites par deux émetteurs

Il faut également prendre en compte le fait que la date de modification et l'origine sont deux attributs rattachés à la station (cf schéma de données pour la date de mise à jour et processus de chargement des données qui s'effectue par station et non par point de recharge). Ceci signifie qu'il ne peut y avoir de panachage entre origine ou entre date de mise à jour (on ne peut pas avoir une station composée de points de recharge avec des dates de mise à jour différentes ou avec des origines différentes).

Une station est donc définie de façon unique par son identifiant, sa date de mise à jour et son origine.
Un point de recharge est défini de façon unique par son appartenance à une station (telle que définie ci-dessous).

## objectif du dédoublonnage

### Dédoublonnage direct

Le dédoublonnage direct doit permettre de ne garder qu'une seule entité pour un identifiant donné. Ce qui revient à choisir une seule date de mise à jour et une seule origine pour une station (puisque les points de recharge se déduisent de la station).

Les critères de choix sont a priori :

- pour les dates : la date la plus récente,
- pour les origines : l'origine avec le meilleur niveau de qualité
Dans les cas les plus compliqués, il y aurait donc à faire un arbitrage entre une entité plus récente mais de moins bonne qualité et une entité de meilleure qualité mais moins récente.

Après dédoublonnage direct, on dispose donc d'une seule station pour un identifiant donné.

### Dédoublonnage indirect

Après le dédoublonnage direct, il reste un deuxième niveau de dédoublonnage à prendre en compte car il concerne le cas fréquent de stations issues de deux origines différentes mais donc les identifiants sont différents (voir exemple EVzen).
Pour ce cas, le dédoublonnage ne peut s'effectuer à partir des identifiants.

On peut alors exploiter les propriétés distinctives qui sont uniques pour une station d'un opérateur, d'une enseigne ou d'un aménageur comme la localisation (coordonnées ou adresse) ou bien le nom de la station :

- deux stations sont des doublons si elles sont d'origine différente et si elles ont une même propriété distinctive (nom_station, adresse_station ou coordonnéeXY) 

Dans ce cas, les mêmes critères de choix que le dédoublonnage direct s'appliquent.

Nota : On peut aussi trouver ce cas entre deux stations d'une même origine. Par exemple, lorsqu'une station change d'unité d'exploitation, ses identifiants sont changés. Dans ce cas, seul le nom de la station est utilisable. L'adresse ou les coordonnées ne sont pas exploitables car on peut trouver plusieurs stations avec une même localisation (cas des parkings multi-niveaux avec une station par niveaux).

## Mise en oeuvre

### Processus

Le processus proposé est le suivant :

- étape 1 : extraction des stations
  - clef d'unicité : id_station_itinerance, date_maj, datagouv_organization_or_owner, 
  - attributs : last_modified, nom_station, adresse_station, coordonnéeXY
- étape 2 : Dédoublonnage direct
  - pour un même id_station_itinerance, éliminer les lignes en double suivant la stratégie définie
- étape 3 : Dédoublonnage indirect
  - pour un même nom_station, adresse_station ou coordonnéeXY, éliminer les lignes en double suivant la stratégie définie
- étape 4 : Filtrer les points de recharge sur la base de la liste résiduelle des stations

### Stratégie de filtrage

Deux options sont envisageables (autres ?) :

- filtrage par date uniquement :
  - pour un id_station_itinerance donné, conservation de la ligne avec date_maj (et en plus last_modified si besoin)
- filtrage par priorité et par date :
  - pour un id_station_itinerance donné, conservation des lignes avec datagouv_organization_or_owner le plus prioritaire
  - si plusieurs lignes, application du filtrage par date.

Le second filtrage revient à privilégier le niveau de qualité sur la "fraicheur".

### Validation d'une méthode de dédoublonnage

Les doublons génèrent des incohérences de structure (contraintes d'intégrité non respectées).
Pour mesurer l'efficacité du dédoublonnage, on peut alors comparer le niveau d'intégrité du jeu de données dédoublonné ([voir exemple](https://github.com/loco-philippe/Environmental-Sensing/blob/test-donnees-vincent/python/Validation/irve/Analyse/analyse_dedoublonnage.ipynb)).
