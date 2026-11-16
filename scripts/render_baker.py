# /// script
# requires-python = ">=3.10, <3.14"
# dependencies = [
#     "pymol-open-source-whl",
# ]
# ///
"""Backwards-compatible wrapper forwarding to render_publication.py."""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from render_publication import main  # noqa: E402

if __name__ == "__main__":
    main()
