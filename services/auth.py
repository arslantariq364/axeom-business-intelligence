"""
Owner authentication and authorization service for Axeom Studio.
Secures administrative and destructive operations in public deployment environments.
"""

import os
from flask import session, request

# Secure Owner PIN / Passcode from environment variable (default for local dev)
OWNER_PIN = os.environ.get("OWNER_PIN", "axeom-owner-2026")


def is_owner_authorized(req=None):
    """
    Checks if the current request or session holds valid owner authorization.
    Accepts:
    1. Active session: session.get('owner_authorized') == True
    2. Header: X-Owner-Auth matching OWNER_PIN
    3. Query / Body parameter in explicit administrative requests
    """
    # 1. Check Flask session
    if session.get("owner_authorized") is True:
        return True

    # 2. Check X-Owner-Auth Header
    current_req = req or request
    if current_req:
        header_pin = current_req.headers.get("X-Owner-Auth")
        if header_pin and header_pin.strip() == OWNER_PIN:
            return True

        # Check JSON body if parsed
        if current_req.is_json:
            try:
                body = current_req.get_json(silent=True) or {}
                body_pin = body.get("owner_pin") or body.get("pin")
                if body_pin and str(body_pin).strip() == OWNER_PIN:
                    return True
            except Exception:
                pass

    return False


def authorize_owner_session(provided_pin: str) -> bool:
    """Validates provided PIN and sets session flag if correct."""
    if not provided_pin:
        return False
    if str(provided_pin).strip() == OWNER_PIN:
        session["owner_authorized"] = True
        return True
    return False


def clear_owner_session():
    """Clears owner authorization from session."""
    session.pop("owner_authorized", None)
