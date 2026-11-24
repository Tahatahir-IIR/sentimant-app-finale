"""La commande « sentiment » : le paquet s'utilise sans connaître ses fichiers.

  sentiment "Livraison rapide, très satisfait"          verdict du modèle (TP 4)
  sentiment --json "Livraison rapide, très satisfait"   le même, en JSON
  sentiment --version
  sentiment predict "texte"                             verdict au contrat de l'API, avec abstention (TP6)
  sentiment serve [--host 127.0.0.1] [--port 8000]      lance l'API
  sentiment ui                                          lance la page Streamlit (l'API doit tourner)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from sentiment_app import __version__

SOUS_COMMANDES = ("predict", "serve", "ui")
VERSION = f"sentiment-app {__version__}"


def _classer(args: argparse.Namespace) -> int:
    """Forme du TP 4 : le verdict brut du modèle (positive ou negative), sans serveur."""
    from sentiment_app.predict import predict

    try:
        r = predict(" ".join(args.texte))
    except ValueError as e:
        print(f"erreur : {e}", file=sys.stderr)
        return 2
    except FileNotFoundError as erreur:
        print(erreur, file=sys.stderr)
        return 1
    print(json.dumps(r, ensure_ascii=False) if args.json else f"{r['label']} (confiance {r['score']:.0%})")
    return 0


def _predire(args: argparse.Namespace) -> int:
    """Même raccord que l'API (api/model.py) : le seuil d'abstention s'applique aussi ici."""
    from api.model import load_model

    try:
        classifieur = load_model()
    except FileNotFoundError as erreur:
        print(erreur, file=sys.stderr)
        return 1
    print(json.dumps(classifieur.predict(" ".join(args.texte)), ensure_ascii=False))
    return 0


def _servir(args: argparse.Namespace) -> int:
    import uvicorn

    uvicorn.run("api.main:app", host=args.host, port=args.port)
    return 0


def _interface(args: argparse.Namespace) -> int:
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print('Streamlit absent : pip install "sentiment-app[ui]"', file=sys.stderr)
        return 1
    page = Path(__file__).resolve().parents[1] / "ui" / "app.py"
    return subprocess.call([sys.executable, "-m", "streamlit", "run", str(page)])


def _parseur_sous_commandes() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sentiment", description="Analyse de sentiment d'avis clients.")
    parser.add_argument("--version", action="version", version=VERSION)
    commandes = parser.add_subparsers(dest="commande", required=True)

    predire = commandes.add_parser("predict", help="classe un avis, sans serveur")
    predire.add_argument("texte", nargs="+", help="l'avis à analyser")
    predire.set_defaults(fonction=_predire)

    servir = commandes.add_parser("serve", help="lance l'API")
    servir.add_argument("--host", default="127.0.0.1")
    servir.add_argument("--port", type=int, default=8000)
    servir.set_defaults(fonction=_servir)

    interface = commandes.add_parser("ui", help="lance la page Streamlit (l'API doit tourner)")
    interface.set_defaults(fonction=_interface)
    return parser


def _parseur_avis() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sentiment", description="Classe le sentiment d'un avis en français.",
        epilog="Autres commandes : sentiment predict, sentiment serve, sentiment ui.")
    parser.add_argument("texte", nargs="+", help="l'avis à classer")
    parser.add_argument("--json", action="store_true", help="sortie JSON")
    parser.add_argument("--version", action="version", version=VERSION)
    parser.set_defaults(fonction=_classer)
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    # Un premier mot predict, serve ou ui désigne une sous-commande ; sinon, c'est l'avis à classer
    parser = _parseur_sous_commandes() if argv and argv[0] in SOUS_COMMANDES else _parseur_avis()
    args = parser.parse_args(argv)
    return int(args.fonction(args))
