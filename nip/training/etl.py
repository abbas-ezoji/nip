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
from .data_access.sql_server import data
from .data_access.db import get_db
from .libs import GA_dataframes, GA_numpy
from .libs.get_random import get_best_first_rank as get_rank
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine

DATABASES = get_db()


class shift():
    def __init__(self,
                 work_section_id=1,
                 year_working_period=139806,
                 coh_day=0.999,  # coh for day requirements const
                 coh_prs=0.001,  # coh for personnel times
                 population_size=80,
                 generations=20,
                 max_const_count=0.3,
                 crossover_probability=0.2,
                 mutation_probability=0.8,
                 elitism=False,
                 show_plot=False,
                 by_parent=True,
                 new=0):
        self.work_section_id = work_section_id
        self.year_working_period = year_working_period
        self.coh_day = coh_day
        self.coh_prs = coh_prs
        self.population_size = population_size
        self.generations = generations
        self.max_const_count = max_const_count
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        self.elitism = elitism
        self.show_plot = show_plot
        self.by_parent = by_parent
        self.new = new
        self.present_id = self.set_present_id()

    def set_present_id(self):
        present_id = (str(self.work_section_id) + '-' + str(self.year_working_period) +
                      '-' + str(int(round(time.time() * 1000))))
        self.present_id = present_id
        return present_id

    def get_present_id(self):

        return self.present_id

    def set_shift(self):
        work_section_id = self.work_section_id
        year_working_period = self.year_working_period
        coh_day = self.coh_day
        coh_prs = self.coh_prs
        population_size = self.population_size
        generations = self.generations
        max_const_count = self.max_const_count
        crossover_probability = self.crossover_probability
        mutation_probability = self.mutation_probability
        elitism = self.elitism
        show_plot = self.show_plot
        by_parent = self.by_parent
        new = self.new
        # -------------------------------------------------------
        PersianYear = int(year_working_period / 100)
        PersianMonth = int(year_working_period % 100)
        # ----------------------- get data -------------------------------------------#
        USER = DATABASES['nip']['USER']
        PASSWORD = DATABASES['nip']['PASSWORD']
        HOST = DATABASES['nip']['HOST']
        # PORT = DATABASES['nip']['PORT']
        NAME = DATABASES['nip']['NAME']

        engine = create_engine('mssql+pyodbc://{}:{}@{}/{}?driver=SQL+Server' \
                               .format(USER,
                                       PASSWORD,
                                       HOST,
                                       NAME
                                       ))