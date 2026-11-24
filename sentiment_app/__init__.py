"""sentiment_app : classer le sentiment d'un avis client en français (modèle, API, interface).

La version suit les TP du cours : 0.N.0 à la fin du TP N, puis 1.0.0 pour la livraison (TP 4).
Elle n'est écrite qu'à un seul endroit, pyproject.toml, et lue ici dans les métadonnées du paquet.
"""
import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from sentiment_app import predict  # le module, appelable : sentiment_app.predict("texte")


def _lire_version() -> str:
    try:
        return version("sentiment-app")
    except PackageNotFoundError:
        # Sources non installées (la CI lance les tests dans le dépôt) : on lit la même source
        pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
        return tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"]


__version__ = _lire_version()
__all__ = ["__version__", "predict"]
