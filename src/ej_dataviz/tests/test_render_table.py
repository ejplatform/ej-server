import pandas as pd
import pytest

from ej_dataviz.tables import render_dataframe


@pytest.fixture
def df():
    d = {'col1': [1, 2], 'col2': [5, 6], 'col3': [9, 10]}

    return pd.DataFrame(data=d)


class TestTable:
    def test_can_render_dataframe(self, df):
        assert str(render_dataframe(df)) == (
            '<div><table id="pandas-table" class="display cell-border compact">'
            '<thead><tr><th class="dt-head-left">col1</th>'
            '<th class="dt-head-left">col2</th>'
            '<th class="dt-head-left">col3</th></tr></thead>'
            '<tbody>'
            '<tr><td>1</td><td>5</td><td>9</td></tr><'
            'tr><td>2</td><td>6</td><td>10</td></tr>'
            '</tbody></table></div>'
        )
