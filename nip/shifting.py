# -*- coding: utf-8 -*-
import sys

import numpy as np
import pandas as pd
import datetime
import time
from data_access.sql_server import data
from libs import GA_dataframes, GA_numpy 
from libs.get_random import get_best_first_rank as get_rank
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine

work_sction_id = 1
year_working_period = 139806

coh_day_req = 0.999         # coh for day requirements const
prs_const = coh_prs = 0.001 # coh for personnel times

population_size=80
generations=200 
max_const_count=0.3

crossover_probability=0.2
mutation_probability=0.8
elitism=False
show_plot=True

by_parent = True
new = False

