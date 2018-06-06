import numpy as np

from hyperpython.components import html_table


def render_dataframe(df, class_=(), datatable=False, **kwargs):
    """
    Convert a Pandas dataframe to a hyperpython structure.
    """
    if datatable:
        class_ = [*class_, 'display', 'cell-border', 'compact']
    data = np.array(df)
    return html_table(data, df.columns, class_=class_, **kwargs)
