from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medbis_price_intelligence.database.base import Base


class Product(Base):
    """A MedBIS product imported from Excel or CSV."""

    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("sku", name="uq_products_sku"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str | None] = mapped_column(String(80), index=True)
    product_name: Mapped[str] = mapped_column(String(400), index=True)
    brand: Mapped[str | None] = mapped_column(String(160), index=True)
    pack_size: Mapped[str | None] = mapped_column(String(120))
    quantity: Mapped[str | None] = mapped_column(String(80))
    strength: Mapped[str | None] = mapped_column(String(120))
    category: Mapped[str | None] = mapped_column(String(160), index=True)
    barcode: Mapped[str | None] = mapped_column(String(80), index=True)
    cost_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    selling_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    source_file: Mapped[str | None] = mapped_column(String(260))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    matches: Mapped[list[Match]] = relationship(back_populates="product")
    price_history: Mapped[list[PriceHistory]] = relationship(back_populates="product")


class Competitor(Base):
    """A configured competitor website."""

    __tablename__ = "competitors"
    __table_args__ = (UniqueConstraint("name", name="uq_competitors_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(260))
    enabled: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    matches: Mapped[list[Match]] = relationship(back_populates="competitor")
    price_history: Mapped[list[PriceHistory]] = relationship(back_populates="competitor")


class Run(Base):
    """A scraper or import run."""

    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_type: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    message: Mapped[str | None] = mapped_column(Text)


class Match(Base):
    """A matched competitor result for a MedBIS product."""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    competitor_id: Mapped[int] = mapped_column(ForeignKey("competitors.id"), index=True)
    competitor_product_name: Mapped[str] = mapped_column(String(400))
    competitor_brand: Mapped[str | None] = mapped_column(String(160))
    competitor_url: Mapped[str | None] = mapped_column(String(600))
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    status: Mapped[str] = mapped_column(String(40), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped[Product] = relationship(back_populates="matches")
    competitor: Mapped[Competitor] = relationship(back_populates="matches")


class PriceHistory(Base):
    """Historical MedBIS and competitor prices."""

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    competitor_id: Mapped[int | None] = mapped_column(ForeignKey("competitors.id"), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[str | None] = mapped_column(String(80))
    captured_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    product: Mapped[Product] = relationship(back_populates="price_history")
    competitor: Mapped[Competitor | None] = relationship(back_populates="price_history")


class Setting(Base):
    """Application setting stored in the database."""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )


class LogEntry(Base):
    """Persistent application log entry."""

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    level: Mapped[str] = mapped_column(String(20), index=True)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ScrapeCache(Base):
    """Cached scraper payload for a competitor search term."""

    __tablename__ = "scrape_cache"
    __table_args__ = (
        UniqueConstraint("competitor_name", "search_term", name="uq_scrape_cache_lookup"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    competitor_name: Mapped[str] = mapped_column(String(120), index=True)
    search_term: Mapped[str] = mapped_column(String(400), index=True)
    payload_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
