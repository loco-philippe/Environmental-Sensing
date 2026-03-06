# Dédoublonnage

Les doublons concernent les points de recharge et les stations.

## Identification des entités

Les entités stations et points de recharge sont identifiés par leur Id (id_pdc_itinerance et id_station_itinerance).

Dans le cas du fichier consolidé IRVE, on peut intègrer des données de plusieurs origines et avec également un historique :

- date de mise à jour (date_maj) : ceci permet de distinguer deux versions d'une même entité
- date de chargement (last_modified) : ceci permet d'identifier le dernier chargement dans les données brutes
- origine (datagouv_organization_or_owner): ceci permet d'identifier deux entités produites par deux émetteurs

Il faut également prendre en compte que :

- la date de modification est un attribut rattaché à la station (cf schéma de données),
- l'origine et la date de chargement sont également deux attribur=ts rattachés à la station de par le processus de chargement des données
Ceci signifie qu'il ne peut y avoir de panachage des points de recharge entre origine, date de mise à jour ou date de chargement (on ne peut pas avoir une station composée de points de recharge avec des dates de mise à jour différentes ou avec des origines différentes).

Une "station instanciée" est donc définie de façon unique par son identifiant, sa date de mise à jour, sa date de chargement et son origine.
Un "point de recharge instancié" est défini de façon unique par son appartenance à une "station instanciée" (telle que définie ci-dessous).

## objectif du dédoublonnage

### Dédoublonnage direct

Le dédoublonnage direct doit permettre de ne garder qu'une seule entité instanciée pour un identifiant donné (point de recharge et station). Ce qui revient à choisir une seule date de mise à jour, une seule date de chargement et une seule origine pour une station. Les points de recharge se déduisent alors de la station instanciée retenue.

Les critères de choix sont a priori :

- pour les dates : la date la plus récente,
- pour les origines : l'origine avec le meilleur niveau de qualité
Dans les cas les plus compliqués, il y aurait donc à faire un arbitrage entre une entité plus récente mais de moins bonne qualité et une entité de meilleure qualité mais moins récente.

Après dédoublonnage direct, on dispose donc d'une seule station instanciée par identifiant de station et d'un seul point de recharge instancié par identifiant de point de recharge.

### Dédoublonnage indirect par origine

Après le dédoublonnage direct, un deuxième niveau de dédoublonnage est à prendre en compte car il concerne le cas fréquent de stations issues de deux origines différentes et dont les identifiants sont différents (voir exemple EVzen).
Pour ce cas, le dédoublonnage ne peut s'effectuer à partir des identifiants.

On peut alors exploiter les propriétés distinctives qui sont uniques pour une station d'un opérateur, d'une enseigne ou d'un aménageur comme la localisation (coordonnées ou adresse) ou bien le nom de la station :

- deux stations sont des doublons si elles sont d'origines différentes et si elles ont une même propriété distinctive (nom_station, adresse_station ou coordonnéeXY)

Dans ce cas, les mêmes critères de choix que le dédoublonnage direct s'appliquent.

Nota : On peut aussi trouver ce cas entre deux stations d'une même origine. Par exemple, lorsqu'une station change d'unité d'exploitation, ses identifiants sont changés. Dans ce cas, seul le nom de la station est utilisable. L'adresse ou les coordonnées ne sont pas exploitables car on peut trouver plusieurs stations avec une même localisation (cas des parkings multi-niveaux avec une station par niveaux).

### Dédoublonnage indirect Qualicharge

Dans Qualicharge, quatre types d'opération impactent le dédoublonnage :

- le décommissionnement partiel qui se traduit par une désactivation d'un point de recharge obsolète,
  Ce cas est traité dans le dédoublonnage direct puisqu'un point de recharge décommissionné n'est pas envoyé par Qualicharge, il a donc une date de mise à jour différente et antérieure aux autres points de recharge.
- le décommissionnement total qui se traduit par une désactivation d'une station obsolète (et de tous les point de recharge),
  à clarifier
- les changements de station qui consistent à déplacer les points de recharge d'une station vers une autre (sans changer d'identifiant des points de recharge)
- les migration d'unité d'exploitation qui se traduisent par la création de nouveaux identifiants tout en gardant les même valeurs d'attributs

( à compléter)

## Mise en oeuvre

### Stratégie de filtrage

Deux options sont envisageables (autres ?) :

- filtrage par date uniquement :
  - pour un identifiant donné, conservation de la ligne avec date_maj (et last_modified) la plus récente
- filtrage par priorité et par date :
  - pour un identifiant donné, conservation des lignes avec datagouv_organization_or_owner le plus prioritaire
  - si plusieurs lignes, application du filtrage par date.

Le second filtrage revient à privilégier le niveau de qualité sur la "fraicheur".

### Processus de dédoublonnage direct

Le processus proposé est le suivant :

- étape 1 : extraction des instances de stations
  - clef d'unicité : id_station_itinerance, date_maj, mast_modified, datagouv_organization_or_owner,
  - élimination des éventuels doublons pour cette clef d'unicité
- étape 2 : Dédoublonnage des stations
  - pour un même id_station_itinerance, élimination les instances de stations suivant la stratégie de filtrage définie
- étape 3 : Dédoublonnage du lien pdc-station
  - pour un même couple id_pdc_itinerance / id_station_itinerance, élimination des instances de couple suivant la stratégie de filtrage définie
- étape 4 : Dédoublonnage des pdc
  - pour un même id_pdc_itinerance élimination des instances de pdc suivant la stratégie de filtrage définie

Le fichier résultant contient alors :

- pour chaque point de recharge une seule ligne,
- pour chaque station un ensemble de lignes avec une même date de mise à jour, une même date de chargement et une même origine.

### Processus de dédoublonnage indirect

Le processus proposé est le suivant :

### Validation d'une méthode de dédoublonnage

Trois types de validation du dédoublonnage
Les doublons génèrent des incohérences de structure (contraintes d'intégrité non respectées).
Pour mesurer l'efficacité du dédoublonnage, on peut alors comparer le niveau d'intégrité du jeu de données dédoublonné ([voir exemple](https://github.com/loco-philippe/Environmental-Sensing/blob/test-donnees-vincent/python/Validation/irve/Analyse/analyse_dedoublonnage.ipynb)).
