"""Test package. Run from the repository root:

    python -m unittest discover -s tests -t .

The modules under test live in src/; some tests share fixtures with each other.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
WEB = REPO / "web"
for path in (SRC, Path(__file__).resolve().parent):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
