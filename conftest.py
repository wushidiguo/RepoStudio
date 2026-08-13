"""Make the skill's scripts importable by the test suite.

The scripts live under `skills/repo-to-video/scripts/` and are not a Python
package, so we add that directory to `sys.path` here.
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent / "skills" / "repo-to-video" / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
