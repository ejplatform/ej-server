import pandas as pd
import numpy as np
import matplotlib.pyplot as plt, mpld3

def test_hist():
    df = pd.DataFrame(np.random.normal(size=(1000, 3)), columns=['a', 'b', 'c'])
    return histogram(df, 'a', 30)


def histogram(data, col, bins):
    """
    Histogram plot.
    """
    data[col].plot.hist(bins=bins)
    fig = plt.gcf()
    d3_figure = mpld3.fig_to_html(fig)
    fig = plt.cla() 
    return d3_figure