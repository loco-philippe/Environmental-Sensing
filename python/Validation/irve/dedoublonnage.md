# Dédoublonnage

Les doublons concernent les points de recharge et les stations.

## Identification des entités

Les entités stations et points de recharge sont identifiés par leur Id (id_pdc_itinerance et id_station_itinerance).
Il faut néanmoins considérer deus autre identifiants :
- date de mise à jour : ceci permet de distinguer deux versions d'une même entité
- origine : ceci permet d'identifier deux entités produites par deux émetteurs

Une station ou un point de recharge est donc défini de façon unique par son identifiant, sa date de mise à jour et son origine.

## objectif du dédoublonnage

Le dédoublonnage 

## Typologie des doublons

### Doublons de points de recharge

Ce niveau est le plus simple. Deux points de recharge sont en doublon lorsqu'il ont le même identifiant id_pdc_itinerance.
Deux sous-cas peuvent être possible :
- même station (définie par son id_station_itinerance)
- stations différentes

### Doublons de station