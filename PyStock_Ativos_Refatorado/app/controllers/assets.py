from __future__ import annotations

import re
import uuid

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database import session_scope
from app.models import AssetUnit, Product, AppSetting


_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}$"
)

class AssetController:
    @staticmethod
    def _parse_qr(payload: str) -> str:
        payload = (payload or "").strip()
        if payload.startswith("PYSTOCK:ASSET:"):
            return payload.split("PYSTOCK:ASSET:", 1)[1].strip()
        return payload

    @staticmethod
    def _looks_like_uuid(value: str) -> bool:
        v = (value or "").strip()
        return bool(_UUID_RE.match(v))

    @staticmethod
    def _generate_asset_tag(session) -> str:
        prefix = (session.get(AppSetting, "patrimony_prefix").value or "").strip()
        width = int(session.get(AppSetting, "patrimony_width").value or "6")
        nxt = session.get(AppSetting, "patrimony_next")
        next_num = int(nxt.value)

        tag = f"{prefix}-{str(next_num).zfill(width)}" if prefix else str(next_num).zfill(width)

        # incrementa e salva
        nxt.value = str(next_num + 1)
        session.add(nxt)
        return tag

    @staticmethod
    def list_assets(search: str = "", status: str = "ALL") -> list[dict]:
        search = (search or "").strip()
        status = (status or "ALL").strip()

        with session_scope() as s:
            q = select(AssetUnit).options(joinedload(AssetUnit.product).joinedload(Product.category))
            if status != "ALL":
                q = q.where(AssetUnit.status == status)

            if search:
                like = f"%{search}%"
                q = q.where(
                    (AssetUnit.asset_tag.ilike(like))
                    | (AssetUnit.serial_number.ilike(like))
                    | (AssetUnit.qr_code.ilike(like))
                )

            rows = s.execute(q.order_by(AssetUnit.id.desc())).scalars().all()
            out = []
            for a in rows:
                out.append(
                    {
                        "id": a.id,
                        "asset_tag": a.asset_tag,
                        "serial": a.serial_number,
                        "serial_number": a.serial_number,
                        "status": a.status,
                        "notes": a.notes,
                        "qr_code": a.qr_code,
                        "product_id": a.product_id,
                        "product": a.product.name if a.product else "",
                        "category": a.product.category.name if (a.product and a.product.category) else "",
                    }
                )
            return out

    @staticmethod
    def get_asset(asset_id: int) -> dict | None:
        with session_scope() as s:
            a = s.execute(select(AssetUnit).options(joinedload(AssetUnit.product).joinedload(Product.category)).where(AssetUnit.id == int(asset_id))).scalars().first()
            if not a:
                return None
            s.refresh(a)
            return {
                "id": a.id,
                "asset_tag": a.asset_tag,
                "serial": a.serial_number,
                        "serial_number": a.serial_number,
                "status": a.status,
                "notes": a.notes,
                "qr_code": a.qr_code,
                "product_id": a.product_id,
                "product": a.product.name if a.product else "",
                "category": a.product.category.name if (a.product and a.product.category) else "",
            }

    @staticmethod
    def get_by_asset_tag(asset_tag: str) -> dict | None:
        asset_tag = (asset_tag or "").strip()
        if not asset_tag:
            return None
        with session_scope() as s:
            a = s.execute(select(AssetUnit).options(joinedload(AssetUnit.product).joinedload(Product.category)).where(AssetUnit.asset_tag == asset_tag)).scalars().first()
            if not a:
                return None
            return {
                "id": a.id,
                "asset_tag": a.asset_tag,
                "serial": a.serial_number,
                        "serial_number": a.serial_number,
                "status": a.status,
                "notes": a.notes,
                "qr_code": a.qr_code,
                "product_id": a.product_id,
                "product": a.product.name if a.product else "",
                "category": a.product.category.name if (a.product and a.product.category) else "",
            }

    @staticmethod
    def get_by_qr(payload: str) -> dict | None:
        qr = AssetController._parse_qr(payload)
        qr = qr.strip()
        if not qr:
            return None
        with session_scope() as s:
            a = s.execute(select(AssetUnit).options(joinedload(AssetUnit.product).joinedload(Product.category)).where(AssetUnit.qr_code == qr)).scalars().first()
            if not a:
                return None
            return {
                "id": a.id,
                "asset_tag": a.asset_tag,
                "serial": a.serial_number,
                        "serial_number": a.serial_number,
                "status": a.status,
                "notes": a.notes,
                "qr_code": a.qr_code,
                "product_id": a.product_id,
                "product": a.product.name if a.product else "",
                "category": a.product.category.name if (a.product and a.product.category) else "",
            }

    @staticmethod
    def get_by_identifier(value: str) -> dict | None:
        value = (value or "").strip()
        if not value:
            return None

        # 1) tenta QR (payload ou UUID)
        if value.startswith("PYSTOCK:ASSET:") or AssetController._looks_like_uuid(value):
            found = AssetController.get_by_qr(value)
            if found:
                return found

        # 2) fallback: patrimônio
        return AssetController.get_by_asset_tag(value)

    @staticmethod
    def create_asset(product_id: int, asset_tag: str | None, serial: str | None, notes: str | None) -> dict:
        with session_scope() as s:
            asset_tag = (asset_tag or "").strip()
            serial = (serial or "").strip() or None
            notes = (notes or "").strip() or None

            if not asset_tag:
                asset_tag = AssetController._generate_asset_tag(s)

            a = AssetUnit(
                product_id=product_id,
                asset_tag=asset_tag,
                serial_number=serial,
                notes=notes,
                status="IN_STOCK",
                qr_code=str(uuid.uuid4()),
            )
            s.add(a)
            s.flush()
            return {"id": a.id, "asset_tag": a.asset_tag, "qr_code": a.qr_code}

    @staticmethod
    def create_assets_bulk(product_id: int, quantity: int, notes: str | None = None) -> list[dict]:
        quantity = int(quantity or 0)
        if quantity <= 0:
            return []
        notes = (notes or "").strip() or None

        created: list[dict] = []
        with session_scope() as s:
            for _ in range(quantity):
                asset_tag = AssetController._generate_asset_tag(s)
                a = AssetUnit(
                    product_id=product_id,
                    asset_tag=asset_tag,
                    serial=None,
                    notes=notes,
                    status="IN_STOCK",
                    qr_code=str(uuid.uuid4()),
                )
                s.add(a)
                s.flush()
                created.append({"id": a.id, "asset_tag": a.asset_tag, "qr_code": a.qr_code})
        return created

    @staticmethod
    def update_asset(asset_id: int, product_id: int, asset_tag: str, serial: str | None, notes: str | None, status: str) -> None:
        with session_scope() as s:
            a = s.execute(select(AssetUnit).options(joinedload(AssetUnit.product).joinedload(Product.category)).where(AssetUnit.id == int(asset_id))).scalars().first()
            if not a:
                raise ValueError("Ativo não encontrado")

            asset_tag = (asset_tag or "").strip()
            if not asset_tag:
                raise ValueError("Patrimônio é obrigatório")

            a.product_id = product_id
            a.asset_tag = asset_tag
            a.serial_number = (serial or "").strip() or None
            a.notes = (notes or "").strip() or None
            a.status = status or a.status
            s.add(a)

    @staticmethod
    def delete_asset(asset_id: int) -> None:
        with session_scope() as s:
            a = s.execute(select(AssetUnit).options(joinedload(AssetUnit.product).joinedload(Product.category)).where(AssetUnit.id == int(asset_id))).scalars().first()
            if not a:
                return
            s.delete(a)
