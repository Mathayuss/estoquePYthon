from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.database import session_scope
from app.models import Category, Supplier, Product, AssetUnit

class CatalogController:
    @staticmethod
    def list_categories() -> list[dict]:
        with session_scope() as s:
            rows = s.execute(select(Category).order_by(Category.name.asc())).scalars().all()
            return [{"id": c.id, "name": c.name} for c in rows]

    @staticmethod
    def create_category(name: str) -> None:
        name = (name or "").strip()
        if not name:
            raise ValueError("Nome da categoria é obrigatório.")
        with session_scope() as s:
            if s.execute(select(Category.id).where(Category.name == name)).first():
                raise ValueError("Categoria já existe.")
            s.add(Category(name=name))

    @staticmethod
    def delete_category(category_id: int) -> None:
        with session_scope() as s:
            c = s.get(Category, int(category_id))
            if not c:
                raise ValueError("Categoria não encontrada.")
            s.delete(c)

    @staticmethod
    def list_suppliers() -> list[dict]:
        with session_scope() as s:
            rows = s.execute(select(Supplier).order_by(Supplier.name.asc())).scalars().all()
            return [{"id": sp.id, "name": sp.name, "cnpj": sp.cnpj, "phone": sp.phone, "email": sp.email} for sp in rows]

    @staticmethod
    def create_supplier(name: str, cnpj: str="", phone: str="", email: str="") -> None:
        name = (name or "").strip()
        if not name:
            raise ValueError("Nome do fornecedor é obrigatório.")
        with session_scope() as s:
            s.add(Supplier(
                name=name,
                cnpj=(cnpj or "").strip() or None,
                phone=(phone or "").strip() or None,
                email=(email or "").strip() or None
            ))

    @staticmethod
    def update_supplier(supplier_id: int, name: str, cnpj: str="", phone: str="", email: str="") -> None:
        name = (name or "").strip()
        if not name:
            raise ValueError("Nome do fornecedor é obrigatório.")
        with session_scope() as s:
            sp = s.get(Supplier, int(supplier_id))
            if not sp:
                raise ValueError("Fornecedor não encontrado.")
            sp.name = name
            sp.cnpj = (cnpj or "").strip() or None
            sp.phone = (phone or "").strip() or None
            sp.email = (email or "").strip() or None

    @staticmethod
    def delete_supplier(supplier_id: int) -> None:
        with session_scope() as s:
            sp = s.get(Supplier, int(supplier_id))
            if not sp:
                raise ValueError("Fornecedor não encontrado.")
            s.delete(sp)

    @staticmethod
    def list_products(search: str="") -> list[dict]:
        search = (search or "").strip()
        with session_scope() as s:
            q = select(Product).options(
                joinedload(Product.category),
                joinedload(Product.supplier),
            ).order_by(Product.name.asc())
            if search:
                like = f"%{search}%"
                q = q.where(Product.name.like(like))
            rows = s.execute(q).scalars().all()

            out = []
            for p in rows:
                stock_count = len(s.execute(
                    select(AssetUnit.id).where(AssetUnit.product_id == p.id, AssetUnit.status == "IN_STOCK")
                ).all())

                out.append({
                    "id": p.id,
                    "name": p.name,
                    "description": p.description or "",
                    "category": p.category.name if p.category else "",
                    "category_id": p.category_id,
                    "supplier": p.supplier.name if p.supplier else "",
                    "supplier_id": p.supplier_id,
                    "cost_price": float(p.cost_price or 0.0),
                    "min_stock": int(p.min_stock or 0),
                    "stock": stock_count,
                })
            return out

    @staticmethod
    def create_product(
        name: str,
        description: str="",
        category_id: int|None=None,
        supplier_id: int|None=None,
        cost_price: float=0.0,
        min_stock: int=0,
    ) -> None:
        name = (name or "").strip()
        if not name:
            raise ValueError("Nome do produto é obrigatório.")
        if min_stock < 0:
            raise ValueError("Estoque mínimo não pode ser negativo.")
        if cost_price < 0:
            raise ValueError("Custo não pode ser negativo.")
        with session_scope() as s:
            s.add(Product(
                name=name,
                description=(description or "").strip() or None,
                category_id=category_id,
                supplier_id=supplier_id,
                cost_price=float(cost_price),
                min_stock=int(min_stock),
            ))

    @staticmethod
    def update_product(
        product_id: int,
        name: str,
        description: str="",
        category_id: int|None=None,
        supplier_id: int|None=None,
        cost_price: float=0.0,
        min_stock: int=0,
    ) -> None:
        name = (name or "").strip()
        if not name:
            raise ValueError("Nome do produto é obrigatório.")
        if min_stock < 0:
            raise ValueError("Estoque mínimo não pode ser negativo.")
        if cost_price < 0:
            raise ValueError("Custo não pode ser negativo.")
        with session_scope() as s:
            p = s.get(Product, int(product_id))
            if not p:
                raise ValueError("Produto não encontrado.")
            p.name = name
            p.description = (description or "").strip() or None
            p.category_id = category_id
            p.supplier_id = supplier_id
            p.cost_price = float(cost_price)
            p.min_stock = int(min_stock)

    @staticmethod
    def delete_product(product_id: int) -> None:
        with session_scope() as s:
            p = s.get(Product, int(product_id))
            if not p:
                raise ValueError("Produto não encontrado.")
            s.delete(p)

    @staticmethod
    def get_dashboard_metrics() -> dict:
        with session_scope() as s:
            products = s.execute(select(Product)).scalars().all()
            total_assets = len(s.execute(select(AssetUnit.id)).all())
            assets_in_stock = len(s.execute(select(AssetUnit.id).where(AssetUnit.status == "IN_STOCK")).all())

            total_value = 0.0
            low_products = []
            for p in products:
                count = len(s.execute(select(AssetUnit.id).where(AssetUnit.product_id == p.id, AssetUnit.status == "IN_STOCK")).all())
                total_value += count * float(p.cost_price or 0.0)
                if count < int(p.min_stock or 0):
                    low_products.append({"id": p.id, "name": p.name, "stock": count, "min_stock": int(p.min_stock or 0)})

            low_products.sort(key=lambda x: x["name"].lower())
            return {
                "total_assets": total_assets,
                "assets_in_stock": assets_in_stock,
                "total_value": float(total_value),
                "low_count": len(low_products),
                "low_products": low_products[:12],
            }


    @staticmethod
    def list_product_stock_summary() -> list[dict]:
        """
        Retorna resumo por Produto/Modelo:
        total e contagem por status (IN_STOCK, OUT, MAINTENANCE, DISPOSED).
        """
        with session_scope() as s:
            # Produtos com categoria
            products = s.execute(
                select(Product).options(joinedload(Product.category)).order_by(Product.name.asc())
            ).scalars().all()

            # Contagem por status
            counts = s.execute(
                select(AssetUnit.product_id, AssetUnit.status, func.count(AssetUnit.id))
                .group_by(AssetUnit.product_id, AssetUnit.status)
            ).all()

            by_prod: dict[int, dict[str, int]] = {}
            for pid, status, c in counts:
                by_prod.setdefault(pid, {})[status] = int(c)

            out = []
            for p in products:
                m = by_prod.get(p.id, {})
                total = sum(m.values())
                out.append({
                    "product_id": p.id,
                    "product": p.name,
                    "category": p.category.name if p.category else "",
                    "min_qty": int(p.min_quantity or 0),
                    "total": total,
                    "in_stock": int(m.get("IN_STOCK", 0)),
                    "out": int(m.get("OUT", 0)),
                    "maintenance": int(m.get("MAINTENANCE", 0)),
                    "disposed": int(m.get("DISPOSED", 0)),
                    "low": int(m.get("IN_STOCK", 0)) < int(p.min_quantity or 0),
                })
            return out
