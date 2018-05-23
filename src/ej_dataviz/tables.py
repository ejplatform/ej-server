import pandas as pd
from bricks.html5 import *

def render_dataframe(df):
    """
    Convert a Pandas dataframe to a hyperpython structure.
    """
    d = {'col1': [1,2,3,4], 'col2':[5,6,7,8], 'col3': [9,10,11,12],
            'col4': ['a','b','c','d'], 'col5': [4,5,2,1]
        }
    test = pd.DataFrame(data=d)
    
    # change test to df after df implementation completes
    return(create_table_base(test).pretty()) 


def create_table_base(df):
    """
    Base method for start a table creation
    """
    columns = df.columns

    return(
        div()[
            table(id="pandas-table", class_="display cell-border compact")[
                create_table_head(columns),
                create_table_body(df)
            ]
        ]
    )


def create_table_head(columns):
    """
    Auxiliar method that creates table heads
    """
    column_list = []
    for i in range(0, len(columns)):
        column_list.append(th(columns[i], class_="dt-head-left"))
        
    return(
        thead()[
            tr()[column_list]
        ]
    )


def create_table_body(df):
    """
    Auxiliar method that creates table body
    """
    main_list = []
    for i in range(0, len(df.index)):
        line_list = []
        for j in range(0, len(df.columns)):
            line_list.append(df.at[df.index[i], df.columns[j]])
        main_list.append(create_table_line(line_list))

    return(
        tbody()[main_list]
    )


def create_table_line(line):
    """
    Auxiliar method that creates table line
    """
    line_list = []
    for i in range(0, len(line)):
        line_list.append(td(str(line[i])))

    return(
        tr()[line_list]
    )