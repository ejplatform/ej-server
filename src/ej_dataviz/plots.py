import pandas as pd
import numpy as np
import matplotlib.pyplot as plt, mpld3

def test_hist():
    df = pd.DataFrame(np.random.normal(size=(1000, 3)), columns=['a', 'b', 'c'])
    df['a'].plot.hist(bins=30)
    fig = plt.gcf()
    d3_figure = mpld3.fig_to_html(fig)
    fig = plt.cla() 
    return d3_figure


def histogram(data):
    """
    Histogram plot.
    """
