import pandas as pd
import numpy as np
import copy
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

# ----------------------- get data -------------------------------------------#
DATABASES = get_db()
USER = DATABASES['nip']['USER']
PASSWORD = DATABASES['nip']['PASSWORD']
HOST = DATABASES['nip']['HOST']
# PORT = DATABASES['nip']['PORT']
NAME = DATABASES['nip']['NAME']

con_string = f'mssql+pyodbc://{USER}:{PASSWORD}@{HOST}/{NAME}?driver=SQL+Server'
engine = create_engine(con_string)
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

PAGE_SIZE = 30

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

import time


def add_sum_shift_len(df):
    sum_shift_len = []
    for row in range(len(df)):
        sum_shifts = 0
        for col in df.columns:
            if col == 'FullName':
                continue
            sh_id = df.loc[row, col]
            if sh_id is None:
                continue
            sh_lenght = shifts_df[shifts_df['id'] == sh_id]['Length'].values[0]
            sum_shifts += sh_lenght
        sum_shifts_t = time.strftime('%H:%M:%S', time.gmtime(sum_shifts))
        sum_shift_len.append(sum_shifts_t)

    sum_shift_len = np.array(sum_shift_len)
    df_sum_shift_len = pd.DataFrame(sum_shift_len, columns=['SumShift'])
    df_sum_shift_len['FullName'] = df['FullName']
    return df_sum_shift_len


df_sum_shift_len = add_sum_shift_len(df)

fig = px.bar(df, x="FullName", y="D01", barmode="group")

table_header = [
    html.Thead(html.Tr([html.Th("First Name"), html.Th("Last Name")]))
]

# import sd_material_ui

app = DjangoDash('simple',
                 meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}]
                 )

app.layout = html.Div([
    dcc.Input(
        id="input",
        placeholder="input type",
        value=1,
        type="hidden"
    ),
    dash_table.DataTable(
        id='table_sum',
        columns=[
            {"name": col, "id": col} for i, col in enumerate(df_sum_shift_len.columns)
        ],
        data=df_sum_shift_len.to_dict('records'),
        style_cell={'textAlign': 'center'},
    ),
    html.Button('تایید و انتقال به دیدگاه', id='submit-val', n_clicks=0),
    dash_table.DataTable(
        id='table',
        columns=[
            {"name": col, "id": col, 'presentation': 'dropdown'} if col != 'FullName' and col != 'sum_shift_len'
            else {"name": col, "id": col} for i, col in enumerate(df.columns)
        ],
        data=df.to_dict('records'),
        dropdown={col: {
            'options': [
                {'label': shift['Title'], 'value': shift['id']}
                for i, shift in shifts_df.iterrows()
            ]
        } if col != 'FullName' and col != 'sum_shift_len' else {} for i, col in enumerate(df.columns)
                  },
        style_cell={'textAlign': 'center', 'maxWidth': 0},
        style_data=[
            {'if': {'row_index': i, 'column_id': 'D01'}, 'background-color': df_colors['COLOR'][i],
             'color': df_colors['COLOR'][i]}
            for i in range(df_colors.shape[0])],
        editable=True,
        # page_current=0,
        # page_size=PAGE_SIZE,
        # page_action='custom'
    ),
    dcc.Graph(
        id='chart-output',
        figure=fig
    )
], style={"height ": "100vh"})


@app.callback(
    Output('table', 'data'),
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
    [Input('table', 'data'),
     Input('table', 'columns')])
def display_chart(rows, columns):
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    # df = add_sum_shift_len(df)
    fig = px.bar(df, x="FullName", y="D01", barmode="group")

    return fig


@app.callback(
    Output('table_sum', 'data'),
    [Input('table', 'data'),
     Input('table', 'columns')])
def display_chart(rows, columns):
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    df_sum_shift_len = add_sum_shift_len(df)
    data = [
        dict(Model=i, **{param: df_sum_shift_len.loc[i, param] for param in df_sum_shift_len.columns})
        for i in range(len(df_sum_shift_len))
    ]

    return data
