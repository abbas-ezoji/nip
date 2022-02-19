import pandas as pd
import dash_core_components as dcc
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
df = pd.read_sql(query.format(1, 1), engine)

PAGE_SIZE = 30

app = DjangoDash('simple')

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

fig = px.bar(df, x="FullName", y="D01", barmode="group")

app.layout = html.Div([
    dcc.Input(
        id="input",
        placeholder="input type",
        value=1,
        type="hidden"
    ),
    dash_table.DataTable(
        id='table',
        columns=[
            {"name": col, "id": col, 'presentation': 'dropdown'} for i, col in enumerate(df.columns)
        ],
        data=df.to_dict('records'),
        dropdown={col: {
            'options': [
                {'label': shift['Title'], 'value': shift['id']}
                for i, shift in shifts_df.iterrows()
            ]
        } if i > 0 else {} for i, col in enumerate(df.columns)
        },

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
    print(value)
    # print(len(df_filtered))
    # print(df['D01'].unique())
    data = [
        dict(Model=i, **{param: df.loc[i, param] for param in df.columns})
        for i in range(len(df))
    ]
    print(data)
    return data


@app.callback(
    Output('chart-output', 'figure'),
    [Input('table', 'data'),
     Input('table', 'columns')])
def display_chart(rows, columns):
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    fig = px.bar(df, x="FullName", y="D01", barmode="group")

    return fig



