from medbis_price_intelligence.importer.detector import ColumnDetector


def test_detector_maps_common_medbis_headers() -> None:
    detector = ColumnDetector()

    mapping = detector.detect(
        [
            "Item Code",
            "Product Description",
            "Manufacturer",
            "Pack",
            "Qty",
            "Strength",
            "Cost",
            "Retail Price",
            "Category",
            "EAN",
        ]
    )

    assert mapping.sku == "Item Code"
    assert mapping.product_name == "Product Description"
    assert mapping.brand == "Manufacturer"
    assert mapping.pack_size == "Pack"
    assert mapping.quantity == "Qty"
    assert mapping.strength == "Strength"
    assert mapping.cost_price == "Cost"
    assert mapping.selling_price == "Retail Price"
    assert mapping.category == "Category"
    assert mapping.barcode == "EAN"

