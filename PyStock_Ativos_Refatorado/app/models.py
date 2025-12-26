from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String, Integer, Float, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class AppSetting(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[str] = mapped_column(String(300), nullable=False)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # admin | operator
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    asset_movements: Mapped[List["AssetMovement"]] = relationship(back_populates="user")

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)

    products: Mapped[List["Product"]] = relationship(back_populates="category")

class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    cnpj: Mapped[Optional[str]] = mapped_column(String(20))
    phone: Mapped[Optional[str]] = mapped_column(String(30))
    email: Mapped[Optional[str]] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    products: Mapped[List["Product"]] = relationship(back_populates="supplier")

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(400))
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)
    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("suppliers.id"), nullable=True)

    # uso interno: manter apenas custo
    cost_price: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    min_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    category: Mapped[Optional[Category]] = relationship(back_populates="products")
    supplier: Mapped[Optional[Supplier]] = relationship(back_populates="products")
    assets: Mapped[List["AssetUnit"]] = relationship(back_populates="product")

    __table_args__ = (CheckConstraint("min_stock >= 0", name="ck_products_min_stock_non_negative"),)

class ExitReason(Base):
    __tablename__ = "exit_reasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    is_active: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    movements: Mapped[List["AssetMovement"]] = relationship(back_populates="reason")

class AssetUnit(Base):
    __tablename__ = "asset_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    asset_tag: Mapped[str] = mapped_column(String(80), nullable=False)
    serial_number: Mapped[Optional[str]] = mapped_column(String(120))
    qr_code: Mapped[str] = mapped_column(String(64), nullable=False)  # uuid
    status: Mapped[str] = mapped_column(String(20), default="IN_STOCK", nullable=False)

    notes: Mapped[Optional[str]] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    product: Mapped["Product"] = relationship(back_populates="assets")
    movements: Mapped[List["AssetMovement"]] = relationship(back_populates="asset")

    __table_args__ = (
        UniqueConstraint("asset_tag", name="uq_asset_units_asset_tag"),
        UniqueConstraint("qr_code", name="uq_asset_units_qr_code"),
        CheckConstraint("status IN ('IN_STOCK','OUT','MAINTENANCE','DISPOSED')", name="ck_asset_units_status"),
    )

class AssetMovement(Base):
    __tablename__ = "asset_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("asset_units.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # IN | OUT
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    reason_id: Mapped[Optional[int]] = mapped_column(ForeignKey("exit_reasons.id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    asset: Mapped["AssetUnit"] = relationship(back_populates="movements")
    reason: Mapped[Optional["ExitReason"]] = relationship(back_populates="movements")
    user: Mapped["User"] = relationship(back_populates="asset_movements")

    __table_args__ = (CheckConstraint("type IN ('IN','OUT')", name="ck_asset_movements_type"),)
