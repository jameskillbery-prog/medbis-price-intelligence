from medbis_price_intelligence.ui.chart import BarChart


def test_bar_chart_exposes_set_data() -> None:
    assert callable(BarChart.set_data)

