import pandas as pd
import numpy as np
import time
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from django_plotly_dash import DjangoDash
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output
import dash_table
from nip.training.data_access.db import get_db
from sqlalchemy import create_engine


def get_zeropad(i, n):
    str_i = str(i)
    zeropad = ''
    for i in range(n - len(str_i)):
        zeropad = zeropad + '0'
    numzeropad = zeropad + str_i

    return numzeropad


def get_day_info_df(df):
    day_info_cols = [col for col in df.columns]
    day_info_cols[0] = 'DayStatistics'
    day_info_df = pd.DataFrame([], columns=day_info_cols)
    day_info_df.at[:, 'DayStatistics'] = ['M', 'A', 'N']

    for col in df.columns:
        if col == 'FullName' or df.loc[0, col] is None:
            continue
        day_info = np.array((df.loc[:, col]).values)
        # print(day_info)
        M = len(day_info[np.logical_or(day_info // 10 == 1, day_info % 10 == 1)])
        A = len(day_info[np.logical_or(day_info // 10 == 2, day_info % 10 == 2)])
        N = len(day_info[np.logical_or(day_info // 10 == 3, day_info % 10 == 3)])
        day_info_df.at[:, col] = [M, A, N]

    return day_info_df


def get_prs_info_df(df):
    sum_shift_len = []
    for i, row in df.iterrows():
        prs_name = row['FullName']
        sum_shifts = 0
        for col in df.columns:
            if col == 'FullName' or col == 'SumShift':
                continue
            sh_id = df.loc[i, col]
            if sh_id is None:
                continue
            sh_lenght = shifts_df[shifts_df['id'] == sh_id]['Length'].values[0]
            sum_shifts += sh_lenght
        sum_shifts_t = time.strftime('%H:%M:%S', time.gmtime(sum_shifts))
        sum_shift_len.append([prs_name, sum_shifts])

    sum_shift_len = np.array(sum_shift_len)
    df_sum_shift_len = pd.DataFrame(sum_shift_len, columns=['FullName', 'sum'])
    return df_sum_shift_len


# ----------------------- get data -------------------------------------------#
DATABASES = get_db()
USER = DATABASES['nip']['USER']
PASSWORD = DATABASES['nip']['PASSWORD']
HOST = DATABASES['nip']['HOST']
# PORT = DATABASES['nip']['PORT']
NAME = DATABASES['nip']['NAME']

con_string = f'mssql+pyodbc://{USER}:{PASSWORD}@{HOST}/{NAME}?driver=SQL+Server'
engine = create_engine(con_string)

query_shifts = '''
SELECT [id]
      ,[Code]
      ,[Title]
      ,[Length]
      ,[StartTime]
      ,[EndTime]
      ,[Type]
      ,[ExternalGuid]
      ,[ExternalId]
  FROM [nip].[dbo].[nip_shifts]
'''

shifts_df = pd.read_sql(query_shifts, engine)
shifts = shifts_df['id'].values
df_colors = pd.DataFrame(data=dict(COLOR=['#1f77b4', '#d62728', '#e377c2', '#17becf', '#bcbd22'],
                                   VALUE=[1, 2, 3, 12, 13]))

query = '''
SELECT 
	  p.FullName
	  ,[D01]      
      ,[D02]
      ,[D03]
      ,[D04]
      ,[D05]
      ,[D06]
      ,[D07]
      ,[D08]
      ,[D09]
      ,[D10]
      ,[D11]
      ,[D12]
      ,[D13]
      ,[D14]
      ,[D15]
      ,[D16]
      ,[D17]
      ,[D18]
      ,[D19]
      ,[D20]
      ,[D21]
      ,[D22]
      ,[D23]
      ,[D24]
      ,[D25]
      ,[D26]
      ,[D27]
      ,[D28]
      ,[D29]
      ,[D30]
      ,[D31]          
  FROM [nip_personnelshiftdateassignments] sh
  join nip_personnel p on p.id = sh.Personnel_id
  where ShiftAssignment_id = {} or 0 = {}
'''
df = pd.read_sql(query.format(4296, 1), engine)
prs_info_df = get_prs_info_df(df)

day_info_df = get_day_info_df(df)

fig = px.bar(df, x="FullName", y="D01", barmode="group")

app = DjangoDash('simple',
                 meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}]
                 )

table_shift = dash_table.DataTable(
    id='table_shift',
    columns=[
        {"name": col, "id": col, 'presentation': 'dropdown'} if col != 'FullName' and col != 'SumShift'
        else {"name": col, "id": col} for i, col in enumerate(df.columns)
    ],
    data=df.to_dict('records'),
    dropdown={col: {
        'options': [
            {'label': shift['Title'], 'value': shift['id']}
            for i, shift in shifts_df.iterrows()
        ]
    } if col != 'FullName' and col != 'SumShift' else {} for i, col in enumerate(df.columns)
              },
    style_cell={'textAlign': 'center', 'maxWidth': 0},
    style_data_conditional=[
        {
            'if': {
                'column_id': 'D' + get_zeropad(i, 2)
            },
            'backgroundColor': 'dodgerblue',
            # 'if': {
            #     'column_id': 'FullName'
            # },
            # 'backgroundColor': 'green',
            'color': 'white'
        } for i, col in enumerate(df.columns)
    ],
    editable=True,
)

table_prs_info = dash_table.DataTable(
    id='table_prs_info',
    columns=[
        {"name": col, "id": col} for i, col in enumerate(prs_info_df.columns)
    ],
    data=prs_info_df.to_dict('records'),
    style_cell={'textAlign': 'center', 'maxWidth': 0},
    style_data_conditional=[
        {
            'if': {
                'row_index': i
            },
            'backgroundColor': 'red',
            'color': 'white'
        } if int(row[1]) > 18000 else {} for i, row in prs_info_df.iterrows()
    ],
)

table_day_info = dash_table.DataTable(
    id='table_day_info',
    columns=[
        {"name": col, "id": col} for i, col in enumerate(day_info_df.columns)
    ],
    data=day_info_df.to_dict('records'),
    style_cell={'textAlign': 'center', 'maxWidth': 0},
),

app.layout = html.Div([
    dcc.Input(
        id="input",
        placeholder="input type",
        value=1,
        type="hidden"
    ),
    html.Table([
        html.Tr([html.Td(table_shift),
                 html.Td(table_prs_info)
                 ]),
        html.Tr([html.Td(table_day_info)])

    ], style={'width': '100%'}),

    dcc.Graph(
        id='chart-output',
        figure=fig
    )
], style={"height ": "100vh"})


@app.callback(
    Output('table_shift', 'data'),
    [Input('input', 'value'), ]
)
def change_output(value):
    df = pd.read_sql(query.format(value, 1), engine)
    data = [
        dict(Model=i, **{param: df.loc[i, param] for param in df.columns})
        for i in range(len(df))
    ]
    # print(data)
    return data


@app.callback(
    Output('chart-output', 'figure'),
    [Input('table_shift', 'data'),
     Input('table_shift', 'columns')])
def display_chart(rows, columns):
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    fig = px.bar(df, x="FullName", y="D01", barmode="group")
    print('display_chart')
    return fig


@app.callback(
    Output('table_prs_info', 'data'),
    [Input('table_shift', 'data'),
     Input('table_shift', 'columns')])
def change_shift_to_prs_info(rows, columns):
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    df = get_prs_info_df(df)
    data = [
        dict(Model=i, **{param: df.loc[i, param] for param in df.columns})
        for i in range(len(df))
    ]

    return data

@app.callback(
    Output('table_day_info', 'data'),
    [Input('table_shift', 'data'),
     Input('table_shift', 'columns')])
def change_shift_to_days_info(rows, columns):
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    df = get_day_info_df(df)
    data = [
        dict(Model=i, **{param: df.loc[i, param] for param in df.columns})
        for i in range(len(df))
    ]

    return data
