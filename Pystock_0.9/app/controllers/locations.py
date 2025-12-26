
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import session_scope
from app.models import Location, AssetUnit

class LocationController:
    @staticmethod
    def list_locations(active_only: bool = False) -> list[dict]:
        with session_scope() as s:
            q = select(Location).order_by(Location.name.asc())
            if active_only:
                q = q.where(Location.is_active == 1)
            rows = s.execute(q).scalars().all()
            return [
                {"id": l.id, "name": l.name, "notes": l.notes, "is_active": int(l.is_active)}
                for l in rows
            ]

    @staticmethod
    def create_location(name: str, notes: str | None = None) -> None:
        name = (name or "").strip()
        if not name:
            raise ValueError("Informe o nome da Unidade (local).")
        notes = (notes or "").strip() or None

        with session_scope() as s:
            s.add(Location(name=name, notes=notes, is_active=1))
            try:
                s.flush()
            except IntegrityError:
                raise ValueError("Já existe uma Unidade com esse nome.")

    @staticmethod
    def update_location(location_id: int, name: str, notes: str | None, is_active: int) -> None:
        name = (name or "").strip()
        if not name:
            raise ValueError("Informe o nome da Unidade (local).")
        notes = (notes or "").strip() or None

        with session_scope() as s:
            loc = s.get(Location, int(location_id))
            if not loc:
                raise ValueError("Unidade não encontrada.")
            loc.name = name
            loc.notes = notes
            loc.is_active = 1 if int(is_active) else 0
            try:
                s.flush()
            except IntegrityError:
                raise ValueError("Já existe uma Unidade com esse nome.")

    @staticmethod
    def delete_location(location_id: int) -> None:
        with session_scope() as s:
            loc = s.get(Location, int(location_id))
            if not loc:
                return
            # bloqueia exclusão se houver equipamentos vinculados
            has_assets = s.execute(select(AssetUnit.id).where(AssetUnit.location_id == int(location_id)).limit(1)).first()
            if has_assets:
                raise ValueError("Não é possível excluir: existem equipamentos vinculados a esta Unidade.")
            s.delete(loc)
