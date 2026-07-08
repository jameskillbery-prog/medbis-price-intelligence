from medbis_price_intelligence.reports.excel import ExcelReportGenerator


def test_report_contains_required_sheet_order() -> None:
    assert ExcelReportGenerator.SHEET_ORDER == [
        "Summary",
        "Competitor Prices",
        "Products Above Market",
        "Margin Opportunities",
        "Historical Prices",
        "Products Without Matches",
    ]

