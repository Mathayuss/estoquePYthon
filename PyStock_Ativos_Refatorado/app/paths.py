from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "PyStockAtivos"

def get_app_data_dir() -> Path:
    """Windows: %APPDATA%\PyStockAtivos. Fallback: ~/AppData/Roaming/PyStockAtivos"""
    base = os.environ.get("APPDATA")
    if base:
        p = Path(base) / APP_NAME
    else:
        p = Path.home() / "AppData" / "Roaming" / APP_NAME
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_db_path() -> Path:
    return get_app_data_dir() / "pystock.db"

def get_exports_dir() -> Path:
    p = get_app_data_dir() / "exports"
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_labels_dir() -> Path:
    p = get_exports_dir() / "labels"
    p.mkdir(parents=True, exist_ok=True)
    return p
