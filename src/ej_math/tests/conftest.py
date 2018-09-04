import numpy as np
import pandas as pd
import pytest

usermap = {1: 'user_a', 3: 'user_b'}


# user, item, choice
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
def votes(data):
    df = pd.DataFrame(data, columns=['user', 'comment', 'choice'])
    df['user'] = list(map(usermap.get, df['user']))
    return df
