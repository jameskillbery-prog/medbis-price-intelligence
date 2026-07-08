from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from medbis_price_intelligence.database.models import Product, Run
from medbis_price_intelligence.database.repositories import ProductRepository
from medbis_price_intelligence.importer.detector import ColumnDetector, ColumnMapping


@dataclass(frozen=True)
class ImportResult:
    """Summary of a product import."""

    source_file: Path
    rows_read: int
    products_saved: int
    mapping: ColumnMapping


class ProductImporter:
    """Imports MedBIS product lists from Excel and CSV files."""

    def __init__(self, session: Session, detector: ColumnDetector | None = None) -> None:
        self.session = session
        self.detector = detector or ColumnDetector()

    def import_file(self, file_path: Path) -> ImportResult:
        """Read a file, detect columns, and save products to SQLite."""
        run = Run(run_type="import", status="running", message=str(file_path))
        self.session.add(run)
        self.session.flush()

        dataframe = self._read_file(file_path)
        mapping = self.detector.detect([str(column) for column in dataframe.columns])
        self._validate_mapping(mapping)

        products = [
            product
            for _, row in dataframe.iterrows()
            if (product := self._row_to_product(row.to_dict(), mapping, file_path)) is not None
        ]

        saved = ProductRepository(self.session).upsert_many(products)
        run.status = "completed"
        run.message = f"Imported {saved} products from {file_path.name}"
        return ImportResult(file_path, len(dataframe.index), saved, mapping)

    @staticmethod
    def _read_file(file_path: Path) -> pd.DataFrame:
        suffix = file_path.suffix.lower()
        if suffix in {".xlsx", ".xls"}:
            return pd.read_excel(file_path)
        if suffix == ".csv":
            return pd.read_csv(file_path)
        raise ValueError("Import file must be an Excel or CSV file.")

    @staticmethod
    def _validate_mapping(mapping: ColumnMapping) -> None:
        if mapping.product_name is None:
            raise ValueError("Could not detect a product name column.")

    def _row_to_product(
        self,
        row: dict[str, Any],
        mapping: ColumnMapping,
        file_path: Path,
    ) -> Product | None:
        product_name = self._clean_text(self._value(row, mapping.product_name))
        if not product_name:
            return None

        return Product(
            sku=self._clean_text(self._value(row, mapping.sku)),
            product_name=product_name,
            brand=self._clean_text(self._value(row, mapping.brand)),
            pack_size=self._clean_text(self._value(row, mapping.pack_size)),
            quantity=self._clean_text(self._value(row, mapping.quantity)),
            strength=self._clean_text(self._value(row, mapping.strength)),
            category=self._clean_text(self._value(row, mapping.category)),
            barcode=self._clean_text(self._value(row, mapping.barcode)),
            cost_price=self._money(self._value(row, mapping.cost_price)),
            selling_price=self._money(self._value(row, mapping.selling_price)),
            source_file=file_path.name,
        )

    @staticmethod
    def _value(row: dict[str, Any], column: str | None) -> Any:
        if column is None:
            return None
        return row.get(column)

    @staticmethod
    def _clean_text(value: Any) -> str | None:
        if value is None or pd.isna(value):
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _money(value: Any) -> Decimal | None:
        if value is None or pd.isna(value):
            return None
        cleaned = str(value).replace("£", "").replace(",", "").strip()
        if not cleaned:
            return None
        try:
            return Decimal(cleaned).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return None

