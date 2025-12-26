from __future__ import annotations
from pathlib import Path
import re
import qrcode

def _safe_filename(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r'[\\/:*?"<>|]+', "_", name)
    return name[:80] if name else "asset"

def generate_asset_qr_png(qr_uuid: str, asset_tag: str, out_dir: str) -> str:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    payload = f"PYSTOCK:ASSET:{qr_uuid}"
    img = qrcode.make(payload)

    filename = f"{_safe_filename(asset_tag)}_{qr_uuid}.png"
    path = out / filename
    img.save(path)
    return str(path)
