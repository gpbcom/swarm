from __future__ import annotations

# Standard library imports
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".claude" / "scripts" / "tickets"


def call(expression: str, setup: str = "") -> object:
    """Evaluate an expression of the ``checks`` module in a child process and return its JSON value."""
    code = (
        f"import sys, json; sys.path.insert(0, {str(SCRIPTS)!r}); import checks; from pathlib import Path\n"
        f"{setup}\nprint(json.dumps({expression}))"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    return json.loads(result.stdout.splitlines()[-1])
