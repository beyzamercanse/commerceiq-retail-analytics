"""Streamlit app smoke test against the populated sample warehouse."""

import pytest
from streamlit.testing.v1 import AppTest

pytestmark = pytest.mark.reporting


def test_revenue_dashboard_renders():
    app = AppTest.from_file("dashboard/app.py").run(timeout=50)
    assert not app.exception
    assert any(metric.label == "Orders" for metric in app.metric)
    assert any(metric.label == "Item GMV" for metric in app.metric)
