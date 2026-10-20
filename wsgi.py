"""WSGI entrypoint for LegalSense Flask API.

Run locally:
    python wsgi.py

Run on Render:
    gunicorn wsgi:app
"""

import os
import sys
from pathlib import Path

# Ensure src/ is on sys.path for direct python wsgi.py invocation
src_dir = str(Path(__file__).resolve().parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from legalsense.api import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
