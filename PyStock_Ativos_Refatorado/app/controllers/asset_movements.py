from __future__ import annotations

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database import session_scope
from app.models import AssetUnit, AssetMovement, ExitReason, User

class AssetMovementController:
    @staticmethod
    def register_in(asset_id: int, user_id: int, notes: str|None=None, occurred_at: datetime|None=None) -> None:
        occurred_at = occurred_at or datetime.utcnow()
        with session_scope() as s:
            a = s.get(AssetUnit, int(asset_id))
            if not a:
                raise ValueError("Ativo não encontrado.")
            u = s.get(User, int(user_id))
            if not u:
                raise ValueError("Usuário não encontrado.")

            if a.status not in ("OUT","MAINTENANCE"):
                raise ValueError(f"Entrada não permitida para status atual: {a.status}")

            a.status = "IN_STOCK"
            s.add(AssetMovement(
                asset_id=a.id,
                type="IN",
                occurred_at=occurred_at,
                reason_id=None,
                notes=(notes or "").strip() or None,
                user_id=u.id
            ))

    @staticmethod
    def register_out(asset_id: int, user_id: int, reason_id: int, notes: str|None=None, occurred_at: datetime|None=None) -> None:
        occurred_at = occurred_at or datetime.utcnow()
        with session_scope() as s:
            a = s.get(AssetUnit, int(asset_id))
            if not a:
                raise ValueError("Ativo não encontrado.")
            u = s.get(User, int(user_id))
            if not u:
                raise ValueError("Usuário não encontrado.")
            r = s.get(ExitReason, int(reason_id))
            if not r or int(r.is_active) != 1:
                raise ValueError("Motivo inválido ou inativo.")

            if a.status != "IN_STOCK":
                raise ValueError(f"Saída não permitida: ativo não está em estoque (status: {a.status})")

            a.status = "OUT"
            s.add(AssetMovement(
                asset_id=a.id,
                type="OUT",
                occurred_at=occurred_at,
                reason_id=r.id,
                notes=(notes or "").strip() or None,
                user_id=u.id
            ))

    @staticmethod
    def list_movements(limit: int=800) -> list[dict]:
        with session_scope() as s:
            q = select(AssetMovement).options(
                joinedload(AssetMovement.asset).joinedload(AssetUnit.product),
                joinedload(AssetMovement.user),
                joinedload(AssetMovement.reason),
            ).order_by(AssetMovement.occurred_at.desc(), AssetMovement.id.desc()).limit(int(limit))

            rows = s.execute(q).scalars().all()
            out = []
            for m in rows:
                a = m.asset
                out.append({
                    "id": m.id,
                    "occurred_at": m.occurred_at,
                    "type": m.type,
                    "asset_tag": a.asset_tag if a else "",
                    "serial_number": a.serial_number if a else "",
                    "product": a.product.name if (a and a.product) else "",
                    "reason": m.reason.name if m.reason else "",
                    "user": m.user.username if m.user else "",
                    "notes": m.notes or "",
                })
            return out
