#!/usr/bin/env python
"""Prédiction unitaire : la fonction que l'API, la commande sentiment et le paquet installé appellent.

Usage :
  python src/predict.py "Livraison rapide, très satisfait"
  >>> import sentiment_app ; sentiment_app.predict("texte")
"""
import os
import sys
import types
from functools import lru_cache
from pathlib import Path
from typing import TypedDict

import joblib

RACINE = Path(__file__).resolve().parents[1]
DANS_LE_DEPOT = RACINE / "models" / "sentiment.joblib"
# Copié dans le paquet au moment de construire la roue (TP 4), jamais commité : voir .gitignore
EMBARQUE = Path(__file__).resolve().parent / "modele" / "sentiment.joblib"


def chemin_modele() -> Path:
    """Où lire le modèle, dans cet ordre :

    1. SENTIMENT_MODELE, si elle est définie : un modèle placé où l'on veut (TP6) ;
    2. models/sentiment.joblib, quand on travaille dans le dépôt ;
    3. le modèle embarqué dans la roue, quand le paquet est installé ailleurs (TP 4).
    """
    if os.environ.get("SENTIMENT_MODELE"):
        return Path(os.environ["SENTIMENT_MODELE"])
    if DANS_LE_DEPOT.exists() or not EMBARQUE.exists():
        return DANS_LE_DEPOT
    return EMBARQUE


MODELE = chemin_modele()


class Prediction(TypedDict):
    """Sortie brute du modèle : ses propres classes, en minuscules."""

    label: str
    score: float


@lru_cache(maxsize=1)
def charger_modele():
    """Chargé une seule fois par processus, pas à chaque appel."""
    if not MODELE.exists():
        raise FileNotFoundError(
            f"modèle introuvable : {MODELE}. Lancez python src/train.py, "
            "ou indiquez son chemin dans la variable SENTIMENT_MODELE"
        )
    return joblib.load(MODELE)


def predict(texte: str) -> Prediction:
    """Renvoie {'label': 'positive'|'negative', 'score': float}."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    pipeline = charger_modele()
    etiquette = pipeline.predict([texte])[0]
    score = float(pipeline.predict_proba([texte]).max())
    return {"label": str(etiquette), "score": round(score, 4)}


class _ModuleAppelable(types.ModuleType):
    """Rend ce module appelable : sentiment_app.predict("texte") appelle la fonction predict.

    Deux kits l'exigent à la fois : le TP 4 appelle sentiment_app.predict(...) comme une fonction,
    les tests du TP6 lisent sentiment_app.predict.chemin_modele et sentiment_app.predict.MODELE
    comme ceux d'un module. Le module reste un module ; il sait seulement aussi se faire appeler.
    """

    def __call__(self, texte: str) -> Prediction:
        return predict(texte)


sys.modules[__name__].__class__ = _ModuleAppelable


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    resultat = predict(" ".join(sys.argv[1:]))
    print(f"{resultat['label']} (confiance {resultat['score']:.0%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
