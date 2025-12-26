from __future__ import annotations
from sqlalchemy import select
from app.database import session_scope
from app.models import ExitReason

class ExitReasonController:
    @staticmethod
    def list_active() -> list[dict]:
        """Alias para listar apenas motivos ativos (compat)."""
        return ExitReasonController.list_reasons(active_only=True)

    @staticmethod
    def list_reasons(active_only: bool = True) -> list[dict]:
        with session_scope() as s:
            q = select(ExitReason).order_by(ExitReason.name.asc())
            if active_only:
                q = q.where(ExitReason.is_active == 1)
            rows = s.execute(q).scalars().all()
            return [{"id": r.id, "name": r.name, "is_active": r.is_active} for r in rows]

    @staticmethod
    def create_reason(name: str) -> None:
        name = (name or "").strip()
        if not name:
            raise ValueError("Nome do motivo é obrigatório.")
        with session_scope() as s:
            if s.execute(select(ExitReason.id).where(ExitReason.name == name)).first():
                raise ValueError("Motivo já existe.")
            s.add(ExitReason(name=name, is_active=1))

    @staticmethod
    def update_reason(reason_id: int, name: str, is_active: int) -> None:
        name = (name or "").strip()
        if not name:
            raise ValueError("Nome do motivo é obrigatório.")
        with session_scope() as s:
            r = s.get(ExitReason, int(reason_id))
            if not r:
                raise ValueError("Motivo não encontrado.")
            r.name = name
            r.is_active = 1 if int(is_active) else 0

    @staticmethod
    def delete_reason(reason_id: int) -> None:
        with session_scope() as s:
            r = s.get(ExitReason, int(reason_id))
            if not r:
                raise ValueError("Motivo não encontrado.")
            s.delete(r)
