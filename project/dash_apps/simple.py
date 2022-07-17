import pandas as pd
import numpy as np
import time
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from django_plotly_dash import DjangoDash
import plotly.graph_objects as go
import dash_daq as daq
import plotly.express as px
from dash.dependencies import Input, Output
import dash_table
from nip.training.data_access.db import get_db
from sqlalchemy import create_engine
from nip import models as nip


def get_zeropad(i, n):
    str_i = str(i)
    zeropad = ''
    for i in range(n - len(str_i)):
        zeropad = zeropad + '0'
    numzeropad = zeropad + str_i

    return numzeropad


def get_time_from_int(h):
    return get_zeropad(h // 60, 2) + ':' + get_zeropad(h % 60, 2)


def get_day_info_df(df):
    day_info_cols = [col for col in df.columns]
    day_info_cols[0] = 'DayStatistics'
    day_info_df = pd.DataFrame([], columns=day_info_cols)
    day_info_df.at[:, 'DayStatistics'] = ['M', 'A', 'N']

    for col in df.columns:
        if col == 'FullName' or col == 'PersonnelNo' or col == 'Post' or df.loc[0, col] is None:
            continue
        day_info = np.array((df.loc[:, col]).values)
        # print(day_info)
        M = len(day_info[np.logical_or(day_info // 10 == 1, day_info % 10 == 1)])
        A = len(day_info[np.logical_or(day_info // 10 == 2, day_info % 10 == 2)])
        N = len(day_info[np.logical_or(day_info // 10 == 3, day_info % 10 == 3)])
        day_info_df.at[:, col] = [M, A, N]

    return day_info_df


def get_prs_info_df(df, value):
    shift_ass_id = value
    shift_ass = nip.ShiftAssignments.objects.get(pk=shift_ass_id)
    sum_shift_len = []
    WorkSection_id, YearWorkingPeriod_id = shift_ass.WorkSection.id, shift_ass.YearWorkingPeriod.id
    for i, row in df.iterrows():
        prs_name = row['FullName']
        prs_no = row['PersonnelNo']
        # prs_speciality = row['ExternalGuid']
        personnel = nip.Personnel.objects.get(PersonnelNo=prs_no,
                                              YearWorkingPeriod__id=YearWorkingPeriod_id, )
        rq_wrk_mins = int(personnel.RequirementWorkMins_esti)
        sum_shifts = 0
        for col in df.columns:
            if col == 'FullName' or col == 'Model' or col == 'PersonnelNo' or col == 'Post':
                continue
            sh_id = df.loc[i, col]
            if sh_id is None:
                continue
            sh_lenght = shifts_df[shifts_df['id'] == sh_id]['Length'].values[0]
            sum_shifts += sh_lenght
        sum_shifts_t = time.strftime('%H:%M:%S', time.gmtime(sum_shifts))
        sum_shift_len.append([get_time_from_int(rq_wrk_mins), get_time_from_int(sum_shifts), sum_shifts,
                              (sum_shifts - rq_wrk_mins) // 60])

    sum_shift_len = np.array(sum_shift_len)
    df_sum_shift_len = pd.DataFrame(sum_shift_len, columns=['FullName', 'sum_hhmm', 'sum', 'Extra'])
    return df_sum_shift_len


def get_DayFullName(d):
    return str(int(d[1:])) + '/' + date_df[date_df['day'] == int(d[1:])]['PersianWeekDayTitleShort']


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
	  ,p.PersonnelNo
	  ,p.ExternalGuid as Post
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
  where ShiftAssignment_id = {} and (0={} or p.PersonnelTypes_id = {} )
  and (0={} or [ExternalGuid] = N'{}')
'''
df = pd.read_sql(query.format(4296, 0, 0, 0, ''), engine)

qry_date = '''
SELECT [PersianDate]
      ,cast(PersianDayOfMonth as int) day
      ,[SpecialDay]
      ,[PersianYear]      
      ,[FiscalYear]
      ,[WorkingPeriodYear]
      ,[WorkingPeriod]            
      ,[PersianWeekDay]
      ,[PersianWeekDayTitle]
      ,[PersianWeekDayTitleShort]
      ,[YearWorkingPeriod_id]
    ,(d.PersianYear*100) + PersianMonth
  FROM 
    [nip_dim_date] d 
    join ETL_YearWorkingPeriod wp on wp.YearWorkingPeriod = (d.PersianYear*100) + PersianMonth
    join nip_shiftassignments s on s.YearWorkingPeriod = wp.Id
WHERE S.id = {}
'''
date_df = pd.read_sql(qry_date.format(4296), engine)

prs_info_df = get_prs_info_df(df, 4296)

day_info_df = get_day_info_df(df)

fig = px.bar(df, x="FullName", y="D01", barmode="group")

app = DjangoDash('simple',
                 external_stylesheets=[dbc.themes.BOOTSTRAP]
                 )

table_shift = dash_table.DataTable(
    id='table_shift',
    columns=[
        {"name": get_DayFullName(col), "id": col,
         'presentation': 'dropdown'} if col != 'FullName' and col != 'PersonnelNo' and col != 'Post'
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
                'column_id': 'D' + get_zeropad(date['day'] * date['SpecialDay'], 2)
            },
            'backgroundColor': 'dodgerblue',
            'color': 'white'
        } for i, date in date_df.iterrows()
    ],
    editable=True,
)

table_prs_info = dash_table.DataTable(
    id='table_prs_info',
    columns=[
        {"name": col, "id": col} for col in ['FullName', 'sum_hhmm', 'Extra']
    ],
    data=prs_info_df.to_dict('records'),
    style_cell={'textAlign': 'center', 'maxWidth': 0},
    style_data_conditional=[
        {
            'if': {
                'filter_query': '{Extra} = {sum}',
            },
            'backgroundColor': 'red',
            'color': 'white'
        }
    ],
)

table_day_info = dash_table.DataTable(
    id='table_day_info',
    columns=[
        {"name": col, "id": col} for i, col in enumerate(day_info_df.columns)
    ],
    data=day_info_df.to_dict('records'),
    style_cell={'textAlign': 'center', 'maxWidth': 0},
)

posts = (
    (0, ("همه")),
    (1, ("حرفه ای")),
    (2, ("غیرحرفه ای")),
)
posts_combo = html.Div([
    dcc.Dropdown(
        id='posts_combo',
        options=[{'label': x[1], 'value': x[0]} for x in posts],
        value=0
    )])

Specialties = pd.unique(df['Post'])
posts_specialities = html.Div([
    dcc.Dropdown(
        id='posts_specialities',
        options=[{'label': x, 'value': x} for x in Specialties],
        value=0
    )])

convert_types = (
    (1, ("با اضافه کاری")),
    (2, ("بدون اضافه کاری")),
)
convert_type_combo = dbc.ButtonGroup(
    [dbc.Button("انتقال با اضافه کاری"), dbc.Button("انتقال بدون اضافه کاری")]

)

daily_const_slider = html.Div([
    daq.Slider(
        id='daily_const_slider',
        value=50
    ),
    html.Div(id='daily_const_slider_label')
])

prs_const_slider = html.Div([
    daq.Slider(
        id='prs_const_slider',
        value=50
    ),
    html.Div(id='prs_const_slider_label')
])

tab_filter = html.Table([
    html.Tr([html.Td(posts_combo), html.Td(posts_specialities)
             ])
], style={'width': '100%'}
)

tab_convert = html.Table([
    html.Tr([convert_type_combo,
             ]),
], style={'width': '100%'}
)

tab_replanner = html.Table([
    html.Tr([html.Td(prs_const_slider),
             html.Td(daily_const_slider)
             ]),
    html.Tr([html.Td(html.Button('بازسازی', id='plan', n_clicks=0), ),
             ])
], style={'width': '100%'}
)

tabs = dcc.Tabs(
    [
        dcc.Tab(tab_filter, label="مدیریت"),
        dcc.Tab(tab_convert, label="انتقال به دیدگاه"),
        dcc.Tab(tab_replanner, label="بازسازی هوشمند شیفت"),
    ]
)

app.layout = dbc.Container(
    html.Div([
        dcc.Input(
            id="input",
            placeholder="input type",
            value=1,
            type="hidden"
        ),
        dcc.Input(
            id="input_test",
            placeholder="input type",
            value=1,
            type="hidden"
        ),
        tabs,
        html.Table([
            html.Tr([html.Td(table_shift),
                     html.Td(table_prs_info)
                     ]),
            html.Tr([html.Td(table_day_info)])

        ], style={'width': '100%'}),
        # dcc.Graph(
        #     id='chart-output',
        #     figure=fig
        # )
    ], style={"height ": "100vh"}))


@app.callback(
    Output('daily_const_slider_label', 'children'),
    [Input('daily_const_slider', 'value')]
)
def sider_daily_const(value):
    return 'درصد ارزش قید روزانه: {}.'.format(value)


@app.callback(
    Output('prs_const_slider_label', 'children'),
    [Input('prs_const_slider', 'value')]
)
def slider_prs_const(value):
    return 'درصد ارزش قید اضافه کاری: {}.'.format(value)


# @app.callback(
#     Output('table_shift', 'data'),
#     [Input('posts_specialities', 'value')]
# )
# def data_table_by_posts_specialities(value):
#     type_value = 0
#     type_filtered = 0
#
#     post_value = value
#     post_filter = 0 if value == 'همه' else 1
#
#     print('data_table_by_posts_specialities')
#     df = pd.read_sql(query.format(init_value, type_filtered, type_value, post_filter, post_value), engine)
#
#     data = [
#         dict(Model=i, **{param: df.loc[i, param] for param in df.columns})
#         for i in range(len(df))
#     ]
#     return data

@app.callback(
    Output('posts_specialities', 'options'),
    [Input('input', 'value'),
     Input('posts_combo', 'value')]
)
def posts_speciality_output(value_input, value_combo):
    global init_value
    init_value = value_input
    type_value = value_combo
    type_filtered = 1 if value_combo else 0

    post_value = 0
    post_filter = 0

    df = pd.read_sql(query.format(init_value, type_filtered, type_value, post_filter, post_value), engine)

    Specialties = ['همه']
    sp_unq = pd.unique(df['Post'])
    [Specialties.append(i) for i in sp_unq]
    print(Specialties)

    return [{'label': x, 'value': x} for x in Specialties]


@app.callback(
    Output('table_shift', 'data'),
    [Input('input', 'value'),
     Input('posts_combo', 'value')]
)
def shift_output(value_input, value_combo):
    global init_value
    init_value = value_input

    type_value = value_combo
    type_filtered = 1 if value_combo else 0

    post_value = 0
    post_filter = 0

    df = pd.read_sql(query.format(init_value, type_filtered, type_value, post_filter, post_value), engine)
    data = [
        dict(Model=i, **{param: df.loc[i, param] for param in df.columns})
        for i in range(len(df))
    ]
    return data


@app.callback(
    Output('chart-output', 'figure'),
    [Input('table_shift', 'data'),
     Input('table_shift', 'columns'),
     Input('input', 'value')])
def display_chart(rows, columns, value):
    df = pd.DataFrame(rows)
    prs_info_df = get_prs_info_df(df, value)
    prs_info_df['sum'] = prs_info_df['sum'].astype('int64') // 60
    fig = px.pie(prs_info_df, names="FullName", values="sum")
    return fig


@app.callback(
    Output('table_prs_info', 'data'),
    [Input('table_shift', 'data'),
     Input('table_shift', 'columns'),
     Input('input', 'value')])
def change_shift_to_prs_info(rows, columns, value):
    df = pd.DataFrame(rows)  # , columns=[c['name'] for c in columns])
    prs_info_df = get_prs_info_df(df, value)
    data = [
        dict(**{param: prs_info_df.loc[i, param] for param in prs_info_df.columns})
        for i in range(len(prs_info_df))
    ]

    return data


@app.callback(
    Output('table_day_info', 'data'),
    [Input('table_shift', 'data'),
     Input('table_shift', 'columns')])
def change_shift_to_days_info(rows, columns):
    df = pd.DataFrame(rows)  # , columns=[c['name'] for c in columns])
    day_info_df = get_day_info_df(df)
    data = [
        dict(**{param: day_info_df.loc[i, param] for param in day_info_df.columns})
        for i in range(len(day_info_df))
    ]

    return data
