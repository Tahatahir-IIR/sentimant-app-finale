# sentiment-app

Classe le sentiment d'un avis client rédigé en français : `positive` ou `negative`, avec une confiance.
Le modèle (TF-IDF puis régression logistique) est embarqué dans le paquet : une seule installation suffit.

## Installer

```bash
pip install sentiment_app-1.0.0-py3-none-any.whl
```

Python 3.11 ou plus. pip installe seul les dépendances, dont scikit-learn 1.5, la seule version avec
laquelle le modèle se relit.

## Utiliser

En Python :

```python
import sentiment_app

sentiment_app.predict("Livraison rapide, produit conforme, très satisfait")
# {'label': 'positive', 'score': 0.777}
```

En ligne de commande :

```bash
sentiment "Livraison rapide, produit conforme, très satisfait"
# positive (confiance 78%)
sentiment --json "Produit cassé et service injoignable, à fuir"
# {"label": "negative", "score": 0.7465}
sentiment --version
```

Un texte vide est refusé : `ValueError` en Python, code de retour 2 en ligne de commande.

Le paquet contient aussi l'API et l'interface du projet : `sentiment serve` lance l'API,
`sentiment ui` la page Streamlit (`pip install "sentiment-app[ui]"`), et `sentiment predict "texte"`
applique le seuil d'abstention de l'API (`INDETERMINE` sous une confiance de 0,60).

Pour utiliser un autre modèle que celui du paquet, indiquez son chemin dans la variable
`SENTIMENT_MODELE`.

## Limites

- Le modèle a appris sur 290 avis de démonstration (F1 macro 0,879 sur 58 avis jamais vus) : il se
  trompe sur les avis qui se retournent (« ..., sauf que ensuite ... ») et ignore les négations.
- La confiance n'est pas une garantie : un humain doit relire les avis douteux. Voir `docs/fiche-modele.md`
  dans le dépôt.
- Un fichier joblib peut exécuter du code à son chargement : n'indiquez dans `SENTIMENT_MODELE` qu'un
  modèle de confiance.
