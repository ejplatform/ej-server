import functools

import pandas as pd
from hyperpython import html

from .tables import render_dataframe

#
# Register table roles
#
html.register(pd.DataFrame, 'table')(render_dataframe)
html.register(pd.DataFrame, 'datatable')(
    functools.partial(render_dataframe, datatable=True)
)
