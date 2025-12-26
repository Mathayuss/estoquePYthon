from __future__ import annotations
from sqlalchemy import select
from app.database import session_scope
from app.models import User
from app.security import verify_password, hash_password

class AuthController:
    @staticmethod
    def login(username: str, password: str) -> dict:
        username = (username or "").strip()
        if not username or not password:
            raise ValueError("Informe usuário e senha.")
        with session_scope() as s:
            user = s.execute(select(User).where(User.username == username)).scalar_one_or_none()
            if not user or not verify_password(password, user.password_hash):
                raise ValueError("Usuário ou senha inválidos.")
            return {"id": user.id, "username": user.username, "role": user.role}

    @staticmethod
    def list_users() -> list[dict]:
        with session_scope() as s:
            rows = s.execute(select(User).order_by(User.username.asc())).scalars().all()
            return [{"id": u.id, "username": u.username, "role": u.role, "created_at": u.created_at} for u in rows]

    @staticmethod
    def create_user(username: str, password: str, role: str) -> None:
        username = (username or "").strip()
        role = (role or "").strip()
        if role not in ("admin", "operator"):
            raise ValueError("Role inválida.")
        if not username or not password:
            raise ValueError("Usuário e senha são obrigatórios.")
        with session_scope() as s:
            if s.execute(select(User.id).where(User.username == username)).first():
                raise ValueError("Usuário já existe.")
            s.add(User(username=username, password_hash=hash_password(password), role=role))

    @staticmethod
    def reset_password(user_id: int, new_password: str) -> None:
        if not new_password:
            raise ValueError("Senha inválida.")
        with session_scope() as s:
            u = s.get(User, int(user_id))
            if not u:
                raise ValueError("Usuário não encontrado.")
            u.password_hash = hash_password(new_password)

    @staticmethod
    def set_role(user_id: int, role: str) -> None:
        role = (role or "").strip()
        if role not in ("admin", "operator"):
            raise ValueError("Role inválida.")
        with session_scope() as s:
            u = s.get(User, int(user_id))
            if not u:
                raise ValueError("Usuário não encontrado.")
            u.role = role
