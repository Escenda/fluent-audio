"""Generate all checked-in fluent-dialogue-dora contract bindings."""
# ruff: noqa: E402

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.generate_contracts import cpp, python, typescript


def main() -> None:
    python.main()
    cpp.main()
    typescript.main()


if __name__ == "__main__":
    main()
