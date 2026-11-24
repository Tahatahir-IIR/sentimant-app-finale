import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

if os.environ.get("VERIFICATION_LIVRABLE"):
    # scripts/verifier_livrable.py (TP 4) teste la roue INSTALLÉE. Le paquet sentiment_app est à la
    # racine du dépôt (TP6), que pytest place dans sys.path : il masquerait la copie installée. On
    # importe donc d'abord celle de site-packages, en retirant le dépôt du chemin le temps de l'import ;
    # les imports suivants réutilisent ce module déjà chargé.
    _chemin = sys.path[:]
    sys.path[:] = [p for p in sys.path if Path(p or ".").resolve() not in (ROOT, ROOT / "src")]
    import sentiment_app  # noqa: E402, F401
    sys.path[:] = _chemin


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def cadrage_dir(root: Path) -> Path:
    return root / "docs" / "cadrage"
