from __future__ import annotations

from contextlib import contextmanager
import shutil
from pathlib import Path

from sqlalchemy import create_engine, select, func, cast, Integer
from sqlalchemy.orm import sessionmaker

from app.models import Base, User, ExitReason, AppSetting, AssetUnit
from app.security import hash_password
from app.paths import get_db_path

DB_PATH = get_db_path()


# Migração simples: se existir banco antigo no diretório do projeto, copia para %APPDATA% na primeira execução
if not DB_PATH.exists():
    project_root = Path(__file__).resolve().parent.parent
    candidates = [
        project_root / "pystock.db",
        project_root / "data" / "pystock.db",
        project_root / "db" / "pystock.db",
    ]
    for c in candidates:
        if c.exists():
            try:
                shutil.copy2(c, DB_PATH)
            except Exception:
                pass
            break


ENGINE = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    future=True,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    Base.metadata.create_all(bind=ENGINE)


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _ensure_setting(session, key: str, default_value: str) -> None:
    cur = session.get(AppSetting, key)
    if not cur:
        session.add(AppSetting(key=key, value=str(default_value)))


def _infer_next_patrimony(session, prefix: str, width: int) -> int:
    """Tenta inferir o próximo número com base nos patrimônios existentes (prefixo-000001 ou 000001)."""
    # SQLite: extrair parte numérica: se começa com prefix-, remove; senão usa inteiro se for só dígitos
    # Estratégia simples: varrer em Python (volume típico é baixo) para evitar SQL complexo.
    rows = session.execute(select(AssetUnit.asset_tag)).all()
    max_n = 0
    for (tag,) in rows:
        if not tag:
            continue
        t = str(tag).strip()
        num_part = None
        if prefix and t.upper().startswith(prefix.upper() + "-"):
            num_part = t.split("-", 1)[1]
        elif t.isdigit():
            num_part = t
        if num_part and num_part.isdigit():
            try:
                n = int(num_part)
                if n > max_n:
                    max_n = n
            except Exception:
                pass
    return max_n + 1 if max_n > 0 else 1


def seed_admin_if_needed() -> None:
    with session_scope() as s:
        # Usuário admin
        if not s.execute(select(User.id)).first():
            s.add(User(username="admin", password_hash=hash_password("admin123"), role="admin"))

        # Motivos padrão
        if not s.execute(select(ExitReason.id)).first():
            for name in [
                "Entrega ao colaborador",
                "Manutenção",
                "Troca",
                "Baixa/Descarte",
                "Uso Interno",
                "Perda",
                "Outro",
            ]:
                s.add(ExitReason(name=name, is_active=1))

        # Settings (patrimônio automático) - robusto mesmo sem flush
        prefix_obj = s.get(AppSetting, "patrimony_prefix")
        if not prefix_obj:
            prefix_obj = AppSetting(key="patrimony_prefix", value="PAT")
            s.add(prefix_obj)

        width_obj = s.get(AppSetting, "patrimony_width")
        if not width_obj:
            width_obj = AppSetting(key="patrimony_width", value="6")
            s.add(width_obj)

        # Definir próximo número com base no que já existe (se ainda não existir)
        nxt = s.get(AppSetting, "patrimony_next")
        if not nxt:
            prefix = (prefix_obj.value or "PAT").strip()
            width = int((width_obj.value or "6").strip())
            next_num = _infer_next_patrimony(s, prefix, width)
            s.add(AppSetting(key="patrimony_next", value=str(next_num)))
