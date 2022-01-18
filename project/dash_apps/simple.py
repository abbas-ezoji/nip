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

df = pd.read_sql('''
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
  where ShiftAssignment_id=4296
''', engine)

PAGE_SIZE = 30

app = DjangoDash('simple')

params = ['FullName', 'D01', 'D02', 'D03', 'D04', 'D05', 'D06', 'D07']

app.layout = html.Div([
    dash_table.DataTable(
        id='table-editing-simple',
        columns=(
            [{'id': p, 'name': p} for p in params]
        ),
        data=[
            dict(Model=i, **{param: 0 for param in params})
            for i in range(1, 5)
        ],
        editable=True
    ),
    dcc.Graph(id='table-editing-simple-output', )
])


@app.callback(
    Output('table-editing-simple-output', 'figure'),
    [Input('table-editing-simple', 'data'),
     Input('table-editing-simple', 'columns')])
def display_output(rows, columns):
    df1 = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    return {
        'data': [{
            'type': 'parcoords',
            'dimensions': [{
                'label': col['name'],
                'values': df1[col['id']]
            } for col in columns]
        }]
    }
