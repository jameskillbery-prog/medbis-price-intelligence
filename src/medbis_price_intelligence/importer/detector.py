from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass(frozen=True)
class ColumnMapping:
    """Detected source columns for a product import."""

    sku: str | None = None
    product_name: str | None = None
    brand: str | None = None
    pack_size: str | None = None
    quantity: str | None = None
    strength: str | None = None
    cost_price: str | None = None
    selling_price: str | None = None
    category: str | None = None
    barcode: str | None = None


class ColumnDetector:
    """Detects likely MedBIS product columns from spreadsheet headers."""

    FIELD_ALIASES: dict[str, tuple[str, ...]] = {
        "sku": ("sku", "item code", "product code", "code", "reference", "ref"),
        "product_name": (
            "product name",
            "name",
            "description",
            "product description",
            "item description",
        ),
        "brand": ("brand", "manufacturer", "make", "supplier brand"),
        "pack_size": ("pack", "pack size", "size", "case size", "unit size"),
        "quantity": ("qty", "quantity", "units", "unit quantity"),
        "strength": ("strength", "dose", "dosage"),
        "cost_price": ("cost", "cost price", "buy price", "purchase price"),
        "selling_price": ("price", "selling price", "retail price", "sell price", "medbis price"),
        "category": ("category", "department", "range", "group"),
        "barcode": ("barcode", "ean", "gtin", "upc"),
    }

    def detect(self, columns: list[str]) -> ColumnMapping:
        """Return a best-effort mapping from spreadsheet headers."""
        normalised = {column: self._normalise(column) for column in columns}
        detected: dict[str, str | None] = {}
        used_columns: set[str] = set()

        for field_name, aliases in self.FIELD_ALIASES.items():
            best_column = None
            best_score = 0.0
            for column, value in normalised.items():
                if column in used_columns:
                    continue
                score = max(self._score(value, alias) for alias in aliases)
                if score > best_score:
                    best_column = column
                    best_score = score

            detected[field_name] = best_column if best_score >= 0.72 else None
            if best_column and best_score >= 0.72:
                used_columns.add(best_column)

        return ColumnMapping(**detected)

    @staticmethod
    def _normalise(value: str) -> str:
        return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").split())

    @staticmethod
    def _score(value: str, alias: str) -> float:
        if value == alias:
            return 1.0
        if alias in value or value in alias:
            return 0.9
        return SequenceMatcher(a=value, b=alias).ratio()

