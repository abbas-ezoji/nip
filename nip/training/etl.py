'''
            <<<<ETL Processes>>>>
    - Fetch data from ERP and other systems
    - Transfer knowledge to ERP system
'''
import sys
# from django.conf import settings

import numpy as np
import pandas as pd
import datetime
import time
from .data_access.sql_server import erp_data as data
from .data_access.db import get_db
from .libs import GA_dataframes, GA_numpy
from .libs.get_random import get_best_first_rank as get_rank
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine

DATABASES = get_db()
USER = DATABASES['erp']['USER']
PASSWORD = DATABASES['erp']['PASSWORD']
HOST = DATABASES['erp']['HOST']
# PORT = DATABASES['nip']['PORT']
NAME = DATABASES['erp']['NAME']

engine = create_engine('mssql+pyodbc://{}:{}@{}/{}?driver=SQL+Server' \
                       .format(USER,
                               PASSWORD,
                               HOST,
                               NAME
                               ))


def update_shift(PersonnelBaseId, Date, ShiftGuid):
    query = ''' UPDATE wc
                SET WorkShiftGuid = CONVERT(uniqueidentifier,{0})
                FROM Didgah_Timekeeper..tkp_WorkCalendarDetails as wc JOIN
                     (
                      SELECT
                          PD.PersonnelBaseId,
                          WCD.*
                      FROM
                          Didgah_Timekeeper..tkp_PersonnelDetails PD
                          JOIN Didgah_Timekeeper..tkp_WorkCalendars WC ON PD.WorkCalendarGuid = WC.Guid
                          JOIN Didgah_Timekeeper..tkp_WorkCalendarDetails WCD ON WCD.WorkCalendarGuid = WC.Guid
                      WHERE
                          WC.Deleted = 0 AND WC.Active = 1
                          AND PD.Deleted = 0 AND PD.[Current] = 1
                          AND PD.PersonnelBaseId = {1}
                          AND WCD.Date = Didgah_Common.dbo.com_udfGetChristianDate({2})
                      ) T ON  T.WorkCalendarGuid = wc.WorkCalendarGuid
                          AND T.Date = wc.Date
            '''.format("'" + ShiftGuid + "'", PersonnelBaseId, "'" + Date + "'")

    with engine.connect() as con:
        con.execute(query)

    return str(PersonnelBaseId) + ' - ' + ShiftGuid + ' - ' + Date


def get_hospital(external_id):
    query = '''SELECT
                    ID, Guid, Title
                FROM
                    Didgah_Common..com_Departments
                WHERE
                    Deleted = 0 AND Code = '1000'
                    AND (ID = {0} OR {0}=0)
                '''.format(external_id)

    hospital_df = pd.read_sql(query, engine)

    return hospital_df


def ETL(YearWorkingPeriod):
    query = '''EXEC [dbo].[etl_RunAllByYearWorkingPeriod] {}
            '''.format(YearWorkingPeriod)

    with engine.connect() as con:
        con.execute(query)

    return 1
