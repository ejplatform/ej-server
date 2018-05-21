import numpy as np
import pandas as pd
import pytest

from ej.ej_math.vote_stats import VoteStats

usermap = {1: 'user_a', 2: 'user_b'}
itemmap = {1: 'item_a', 2: 'item_b', 3: 'item_c'}


# user, item, vote
@pytest.fixture
def data():
    return np.array([
        [1, 1, 1],
        [1, 2, 1],
        [1, 3, 0],
        [3, 1, 1],
        [3, 2, -1],
    ])


@pytest.fixture
def df(data):
    return pd.DataFrame(data, columns=['user', 'comment', 'vote'])


class TestStatsClass:
    def test_user_stats(self, df):
        st = VoteStats(df, total=3, cols=['user', 'vote'])

        assert len(st.data) == 5
        assert len(st.filtered) == 4
        assert all(st.skip == [1, 0])
        assert all(st.missing == [0, 1])
        assert all(st.count == [3, 2])
        assert all(st.count_filtered == [2, 2])
        assert all(st.average == [3 / 2, 0])
        assert all(st.average_filtered == [1, 0])

    def test_item_stats(self, df):
        st = VoteStats(df, total=2, cols=['comment', 'vote'])

        assert len(st.data) == 5
        assert len(st.filtered) == 4
        assert all(st.missing == [0, 0, 1])
        assert all(st.skip == [0, 0, 1])
        assert all(st.count == [2, 2, 1])
        assert all(st.count_filtered == [2, 2, 0])
        assert all(st.average == [1, 0, 0])
        assert all(st.average_filtered == [1, 0, 0])
