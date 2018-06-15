from ej_math.data import VoteStats


class TestStatsClass:
    def test_user_stats(self, df):
        st = VoteStats(df, cols=['user', 'vote'])

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
