"""Run without installing the package: python scripts/preview.py demo ..."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vec_mobility.cli import main

if __name__ == "__main__":
    main()

