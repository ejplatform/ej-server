import numpy as np

from hyperpython.components import html_table


def render_dataframe(df, index=False, *, datatable=False, class_=(),
                     col_display=None, **kwargs):
    """
    Convert a Pandas dataframe to a hyperpython structure.

    Args:
        df (DataFrame):
            Input data frame.
        col_display (map):
            An optional mapping from column names in a dataframe to their
            corresponding human friendly counterparts.
        datatable (bool):
            If True, prepare data to be handled by the Data table js library.

    Additional attributes (such as class, id, etc) can be passed as keyword
    arguments.
    """
    if datatable:
        class_ = [*class_, 'display', 'cell-border', 'compact']

    data = np.array(df.astype(object))
    columns = df.columns

    if index:
        data = np.hstack([df.index[:, None], df])
        columns = [df.index.name or '', *columns]

    columns = as_display_values(columns, col_display)
    return html_table(data, columns, class_=class_, **kwargs)


def as_display_values(seq, translations=None):
    if translations is None:
        return list(map(str, seq))
    else:
        return [str(translations.get(x, x)) for x in seq]
