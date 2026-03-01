# Dédoublonnage

Les doublons concernent les points de recharge et les stations.

## Identification des entités

Les entités stations et points de recharge sont identifiés par leur Id (id_pdc_itinerance et id_station_itinerance).
Il faut néanmoins considérer deux autres identifiants :
- date de mise à jour : ceci permet de distinguer deux versions d'une même entité
- origine : ceci permet d'identifier deux entités produites par deux émetteurs

Une station ou un point de recharge est donc défini de façon unique par son identifiant, sa date de mise à jour et son origine.
Il faut également prendre en compte le fait que la date de modification et l'origine sont deux attributs rattachés à la station (cf schéma de données pour la date de mise à jour et processus de chargement des données qui s'effectue par station et non par point de recharge). Ceci signifie qu'il ne peut y avoir de panachage entre origine et date de mise à jour (on ne peut pas avoir une station composée de points de recharge avec des dates de mise à jour différentes ou avec des origines différentes.

## objectif du dédoublonnage

### Dédoublonnage direct

Le dédoublonnage doit permettre de ne garder qu'une seule entité pour un identifiant donné. Ce qui revient à choisir une seule date de mise à jour et une seule origine pour une station (puisque les points de recharge "héritent" de l'origine et de la date de mise à jour).
Les critères de choix sont a priori :
- pour les dates : la date la plus récente,
- pour les origines : l'origine avec le meilleur niveau de qualité
Dans les cas les plus compliqués, il y aurait donc à faire un arbitrage entre une entité plus récente mais de moins bonne qualité et une entité de meilleure qualité mais moins récente.

Après dédoublonnage, on dispose donc d'une seule station pour un identifiant donné.

Cependant, après ce premier dédoublonnage, il reste un deuxième niveau de dédoublonnage à prendre en compte car il concerne un cas fréquent : le cas des stations issues de deux origines différentes mais donc les identifiants sont différents. Pour ce second cas, le dédoublonnage ne peut s'effectuer à partir des identifiants.
Pour traiter ce cas, on peut utiliser la notion de localisation il faut prendre en compte un autre niveau de regroupement qui est la localisation. 

## Typologie des doublons

### Doublons de points de recharge

Ce niveau est le plus simple. Deux points de recharge sont en doublon lorsqu'il ont le même identifiant id_pdc_itinerance.
Deux sous-cas peuvent être possible :
- même station (définie par son id_station_itinerance)
- stations différentes

### Doublons de station