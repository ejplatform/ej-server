import pandas as pd
import pytest

from ej_dataviz.tables import render_dataframe


@pytest.fixture
def df():
    return pd.DataFrame({'col1': [1, 2], 'col2': [3, 4], 'col3': [5, 6]})


class TestTable:
    def test_can_render_dataframe(self, df):
        assert str(render_dataframe(df)) == (
            '<table>'
            '<thead><tr><th>col1</th><th>col2</th><th>col3</th></tr></thead>'
            '<tbody>'
            '<tr><td>1</td><td>3</td><td>5</td></tr>'
            '<tr><td>2</td><td>4</td><td>6</td></tr>'
            '</tbody></table>'
        )
