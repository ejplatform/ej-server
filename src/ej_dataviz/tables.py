import pandas as pd

from hyperpython import table, div, td, tr, th, tbody, thead


def test():
    d = {'col1': [1, 2, 3, 4], 'col2': [5, 6, 7, 8], 'col3': [9, 10, 11, 12],
         'col4': ['a', 'b', 'c', 'd'], 'col5': [4, 5, 2, 1]
         }
    test = pd.DataFrame(data=d)

    # change test to df after df implementation completes
    return (render_dataframe(test))


def render_dataframe(df):
    """
    Convert a Pandas dataframe to a hyperpython structure.
    """
    columns = df.columns

    return (
        div()[
            table(id="pandas-table", class_="display cell-border compact")[
                create_table_head(columns),
                create_table_body(df)
            ]
        ]
    )


def create_table_head(columns, align='left'):
    # Auxiliar method that creates table heads
    class_ = "dt-head-left"  # todo: personalizar!
    column_list = [th(col, class_=class_) for col in columns]
    return thead()[
        tr()[column_list]
    ]


def create_table_body(df):
    # Auxiliar method that creates table body
    main_list = []
    for i in range(0, len(df.index)):
        line_list = []
        for j in range(0, len(df.columns)):
            line_list.append(df.at[df.index[i], df.columns[j]])
        main_list.append(create_table_line(line_list))

    return (
        tbody()[main_list]
    )


def create_table_line(lines):
    # Auxiliar method that creates table line
    line_list = [td(str(li)) for li in lines]

    return (
        tr()[line_list]
    )
