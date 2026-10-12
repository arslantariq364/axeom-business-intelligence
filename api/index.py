"""
Vercel Serverless WSGI Entry Point for Axeom Dashboard.
Exposes the Flask WSGI application for the Vercel Python runtime.
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app

# Production WSGI application instance
app.debug = False
