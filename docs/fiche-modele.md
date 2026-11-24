# Fiche modèle : sentiment-app

## Identité du modèle

`tfidf-logreg`, livré avec le paquet `sentiment_app` en version 1.0.0. Le modèle est un pipeline scikit-learn (1.5.2) en deux étages : un vectoriseur TF-IDF (mots et paires de mots, `min_df=2`, 316 termes) suivi d'une régression logistique (`class_weight="balanced"`, graine 42). Il a été entraîné le 2026-10-21 sur le jeu de démonstration et sauvegardé dans `models/sentiment.joblib`.

## Usage prévu

Trier chaque jour les avis clients rédigés en français, pour que l'équipe du service client réponde d'abord aux avis négatifs. Le modèle propose un verdict (`POSITIVE`, `NEGATIVE`) avec une confiance, et l'API répond `INDETERMINE` sous 0,60 : ces avis-là sont relus par un agent. Il s'agit d'aider à prioriser, la décision finale reste à l'agent.

## Usages exclus

- Juger un client ou un salarié : le verdict porte sur un texte et ne dit rien de la personne qui l'a écrit.
- Publier, masquer ou supprimer un avis automatiquement, sans relecture.
- Classer des textes dans une autre langue, ou d'un autre domaine que la relation client (critiques de films, messages internes) : le vocabulaire appris ne les couvre pas.
- Décider d'un remboursement ou d'une sanction sur la seule foi du verdict.

## Données d'entraînement

290 avis de démonstration en français (`data/demo_reviews.csv`, régénérés par `src/train.py`) : 145 positifs et 145 négatifs, découpés de façon stratifiée (graine 42) en 232 avis d'entraînement et 58 avis de test, mis de côté avant d'apprendre le vocabulaire. Ce sont des avis courts sur la livraison, l'emballage et le service. Ces données ne couvrent ni l'ironie, ni les négations (« ne… pas »), ni les avis longs et nuancés, ni les autres domaines. Le jeu Allociné (20 000 critiques de films) a seulement servi de comparaison, pas à entraîner le modèle livré.

## Performances mesurées

Valeurs de `models/metrics.json`, mesurées sur les 58 avis de test : F1 macro 0.879 (le seuil fixé au TP1 est 0,85), exactitude 0,879 (51 avis justes sur 58), rappel des négatifs 0.931 (27 mécontents retrouvés sur 29). Matrice de confusion : 27 négatifs justes, 2 négatifs classés positifs, 5 positifs classés négatifs, 24 positifs justes. Avec le seuil d'abstention de l'API à 0,60, le modèle répond à 42 avis sur 58 (72 %), avec une exactitude de 0,952 et 2 erreurs restantes au lieu de 7 ; les 16 autres avis (28 %) partent vers un humain.

## Limites connues

Le modèle ne tient pas compte de l'ordre des mots. Les 7 erreurs du jeu de test sont toutes des avis qui se retournent : « Taille trop petite et retour payant au déballage, sauf que ensuite produit conforme à la description, très satisfait » est classé negative avec une confiance de 0,5335, alors qu'il est positif. Il ignore aussi la négation : sur le jeu d'or, « Je ne suis pas satisfait, le produit ne fonctionne pas » reçoit POSITIVE à 0,67, parce que « satisfait » pèse plus que « ne pas ». Enfin, un texte sans aucun mot connu reçoit toujours la même probabilité (0,5162, seule l'ordonnée à l'origine compte). L'API s'abstient alors, mais aussi sur des avis faciles dont le vocabulaire est absent des 316 termes, comme « Commande reçue en deux jours, emballage soigné » à 0,52.

## Biais mesurés

Résultats de `python src/biais.py` sur les 58 avis de test, au seuil de 0,60. Le groupe le moins bien servi est celui des avis avec retournement : 17 avis, exactitude 0,588, 7 erreurs, dont 15 avis envoyés vers un humain. Les avis directs, eux, obtiennent 41 avis justes sur 41. Les avis longs paraissent moins bien servis (27 avis, 0,741), mais la longueur n'est pas la cause : les 10 avis longs sans retournement sont tous justes. Ces effectifs sont petits (17 avis), il faudra donc confirmer ces écarts sur un plus grand jeu.

## Explicabilité

Comme le modèle est linéaire, `python src/expliquer.py` (SHAP) décompose exactement sa sortie : valeur de base -0,0114 plus les contributions de chaque terme, ce qui redonne -0,1343, la sortie du modèle sur l'avis mitigé. Parmi les termes les plus influents, on trouve des mots porteurs de sentiment (« cassé » -0,923, « impeccable » +0,677), mais aussi des mots-outils : « je » (+0,771), « en » (+0,683), « au » (-0,689). Le modèle a donc appris des tournures propres au jeu de démonstration, pas seulement du sentiment. Sur l'avis mitigé, les 20 termes négatifs (-1,0061) l'emportent de peu sur les 13 termes positifs (+0,9177).

## Conditions d'usage

Un humain relit tous les avis `INDETERMINE` (confiance sous 0,60, environ 28 % des avis), ainsi que les avis contenant une négation ou un retournement (« mais », « sauf que », « finalement »), même quand le modèle tranche. Aucune réponse au client, aucun remboursement et aucune suppression d'avis ne se décide sur la seule foi du verdict. Les avis classés positifs sont aussi relus par échantillon, puisque 2 mécontents sur 29 y échappent encore.

## Maintenance

Réentraîner avec `python src/train.py` dès que de nouveaux avis étiquetés sont disponibles, ou si le rappel des négatifs passe sous 0,90 lors d'un contrôle mensuel. Le modèle doit être réentraîné et chargé avec scikit-learn 1.5 (épinglé dans le paquet et dans la CI), car un `joblib` change de format d'une version à l'autre. Le modèle est embarqué dans la roue : avant `python -m build`, il faut copier le nouveau `models/sentiment.joblib` dans `sentiment_app/modele/`, puis republier une version. Pour en utiliser un autre sans republier, on indique son chemin au paquet par la variable `SENTIMENT_MODELE`. Après chaque réentraînement, il faut mettre à jour cette fiche et `models/metrics.json` ; `tests/test_fiche_modele.py` échoue si les chiffres cités ne sont plus ceux du dépôt.
