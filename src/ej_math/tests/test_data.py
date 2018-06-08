import numpy as np

from ej_math import VoteStats


class TestStatsClass:
    def test_user_stats(self, votes):
        st = VoteStats(votes)
        df = st.users()
        print(df)
        assert list(df.columns) == ['votes', 'missing', 'skipped', 'agree',
                                    'disagree', 'average', 'divergence', 'entropy']
        assert list(df.votes) == [3, 2]
        assert list(df.missing) == [0, 1 / 3]
        assert list(df.skipped) == [1 / 3, 0]
        assert list(df.agree) == [1, .5]
        assert list(df.disagree) == [0, .5]
        assert list(df.average) == [2 / 3, 0]
        assert list(df.divergence) == [1, 0]
        assert list(df.entropy) == [0, 0.6931471805599453]

    def test_comment_stats(self, votes):
        st = VoteStats(votes)
        df = st.comments()
        print(df)
        assert list(df.votes) == [2, 2, 1]
        assert list(df.missing) == [0, 0, .5]
        assert list(df.skipped) == [0, 0, 1]
        assert list(df.agree) == [1, .5, 0]
        assert list(df.disagree) == [0, .5, 0]
        assert list(df.average) == [1, 0, 0]
        assert list(df.divergence)[:2] == [1, 0]
        assert not np.isfinite(list(df.divergence)[-1])
        assert list(df.entropy) == [0, 0.6931471805599453, 0]

    def test_percentage_df(self, votes):
        df = VoteStats(votes).users(pc=True)
        assert list(df.agree) == [100, 50]

    def test_override_number_of_votes(self, votes):
        df = VoteStats(votes, n_users=10, n_comments=4).users()
        assert list(df.missing) == [.25, .5]
        assert list(df.agree) == [1, .5]

    def test_can_load_from_raw_data(self, data, votes):
        check = VoteStats(data).votes == votes
        assert np.all(check['comment'])
        assert np.all(check['choice'])

    def test_pivot_table(self, votes):
        table = [
            [1, 1, 0],
            [1, -1, float('nan')],
        ]
        np.testing.assert_equal(np.array(VoteStats(votes).pivot_table), table)
