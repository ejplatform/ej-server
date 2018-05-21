import pandas as pd
import pytest


@pytest.fixture
def df():
    return pd.DataFrame([])


class TestTable:
    def test_can_render_dataframe(self, df):
        ...
        assert 40 < 2
