'''
            <<<<Shift Recommandeation by Genetic Algorithm>>>>
    - Create initial gene by pivot table
    - Fetch Personnel, Shift and WorkSection Requirements Info
'''
import sys
# from django.conf import settings

import numpy as np
import pandas as pd
import datetime
import time
from .data_access.sql_server import nip_data as data
from .data_access.db import get_db
from .libs import GA_dataframes, GA_numpy
from .libs.get_random import get_best_first_rank as get_rank
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine

DATABASES = get_db()

# ----------------------- get data -------------------------------------------#
USER = DATABASES['nip']['USER']
PASSWORD = DATABASES['nip']['PASSWORD']
HOST = DATABASES['nip']['HOST']
# PORT = DATABASES['nip']['PORT']
NAME = DATABASES['nip']['NAME']

con_string = f'mssql+pyodbc://{USER}:{PASSWORD}@{HOST}/{NAME}?driver=SQL+Server'
engine = create_engine(con_string)


class shift():
    def __init__(self,
                 work_section_id=1,
                 year_working_period=4,
                 year_working_period_value=139911,
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
                 new=0,
                 rec_id=1059):
        print(f'work_section_id: {work_section_id} year_working_period: {year_working_period_value}')
        self.work_section_id = work_section_id
        self.year_working_period = year_working_period
        self.year_working_period_value = year_working_period_value
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
        self.rec_id = rec_id


    def set_present_id(self):
        present_id = (str(self.work_section_id) + '-' + str(self.year_working_period_value) +
                      '-' + str(int(round(time.time() * 1000))))
        self.present_id = present_id
        return present_id

    def get_present_id(self):

        return self.present_id

    def set_shift(self):
        work_section_id = self.work_section_id
        year_working_period = self.year_working_period
        year_working_period_value = self.year_working_period_value
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
        rec_id = self.rec_id
        # -------------------------------------------------------
        PersianYear = int(year_working_period_value / 100)
        PersianMonth = int(year_working_period_value % 100)

        query_gene_last = '''SELECT TOP 1   
                                       [Rank]
                                   ,[Cost]      
                                   ,[WorkSection_id]
                                   ,[YearWorkingPeriod]
                                   ,[EndTime]
                                   ,0 life_cycle	 
                                   ,[UsedParentCount]
                             FROM [nip_shiftassignments]                         
                             WHERE WorkSection_id = {0} AND YearWorkingPeriod = {1}                                
                             ORDER BY [Rank]
                           '''.format(work_section_id, year_working_period)

        parent_rank = get_rank(engine, query_gene_last)

        query_gene_last = '''SELECT st.[Personnel_id]
                              ,st.[YearWorkingPeriod]
                              ,[D01],[D02],[D03],[D04],[D05],[D06]
                              ,[D07],[D08],[D09],[D10],[D11],[D12]
                              ,[D13],[D14],[D15],[D16],[D17],[D18]
                              ,[D19],[D20],[D21],[D22],[D23],[D24]
                              ,[D25],[D26],[D27],[D28],[D29],[D30],[D31]
                            FROM 
                                [nip_shiftassignments] S
                                JOIN [nip_personnelshiftdateassignments] ST 
                                ON ST.ShiftAssignment_id = S.id
                            WHERE                           	
                                WorkSection_id = {0}                      
                                AND S.YearWorkingPeriod = {1}   
                                AND S.RANK = {2}
                         '''.format(work_section_id,
                                    year_working_period,
                                    parent_rank)

        query_gene_new = '''SELECT 
                                 p.id Personnel_id     					 
                                ,YearWorkingPeriod
                                ,PersianDayOfMonth as Day
                                ,1 Shift_id
                            FROM 
                                nip_Personnel P JOIN
                                nip_Dim_Date D ON D.PersianYear = {0} 
                                AND PersianMonth={1} and WorkSection_id = {2}
                          '''.format(PersianYear, PersianMonth, work_section_id)

        query_personnel = '''SELECT  id [Personnel_id]
                                    ,[WorkSection_id]
                                    ,[YearWorkingPeriod]
                                    ,[RequirementWorkMins_esti]
                                    ,[PersonnelTypes_id] prs_typ_id
                                    ,[EfficiencyRolePoint]
                            FROM [nip_Personnel]
                            WHERE WorkSection_id = {0} AND YearWorkingPeriod = {1}
                          '''.format(work_section_id, year_working_period)

        query_hard_const = '''SELECT P.[YearWorkingPeriod]
                              ,isnull([Day], d.PersianDayOfMonth)[Day]
                              ,[Personnel_id]
                              ,l.[Value]
                              ,l.ShiftType_id
                        FROM [nip_hardconstraints] l join 
                             [nip_personnel] p on p.id=l.Personnel_id
                        	 JOIN nip_Dim_Date D ON D.PersianYear = 1400 AND D.PersianMonth = 04 
                        	 AND (L.Day = D.PersianDayOfMonth OR L.Day IS NULL)
                          WHERE P.WorkSection_id = {} AND P.YearWorkingPeriod = {}
                          '''.format(work_section_id, year_working_period)

        query_shift = '''SELECT [id] as Shift_id
                             ,Code ShiftCode
                             ,[Title]
                             ,[Length]
                             ,[StartTime]
                             ,[EndTime]
                             ,cast([Type] as int) shift_type_id
                        FROM [nip_Shifts]
                     '''
        query_shift_req = '''SELECT [PersianDayOfMonth] AS Day                          
                                  ,[PersonnelTypeReq_id] as prs_typ_id
                                  ,CAST(SHT.Code AS INT) shift_type_id
                                  ,[ReqMinCount]
                                  ,[ReqMaxCount]
                                  ,[day_diff_typ]
                            FROM 
                                [nip_WorkSectionRequirements] R
								join etl_yearworkingperiod wp on wp.id = r.yearWorkingperiod
                                JOIN nip_dim_date D ON D.PersianYear=wp.yearworkingperiod/100
                                AND D.PersianMonth = wp.yearworkingperiod%100          
                                JOIN nip_shifttypes SHT ON SHT.ID = R.ShiftType_id              	
                            WHERE 
                                r.YearWorkingPeriod= {}
                                AND WorkSection_id = {}
                            ORDER BY 
                                WorkSection_id,D.PersianDate
                                ,PersonnelTypeReq_id,ShiftType_id                        
        
                          '''.format(year_working_period, work_section_id)
        query_prs_req = '''SELECT  [Personnel_id] 
                                  ,p.[YearWorkingPeriod]
                                  ,p.[WorkSection_id]
                                  ,[Day]
                                  ,[ShiftType_id] as shift_type_id
                                  ,[Value]
                          FROM [nip_selfdeclaration] r join [nip_personnel] p
                               on p.id = r.Personnel_id
                          WHERE p.[WorkSection_id] = {0}
                                and p.[YearWorkingPeriod] = {1}
                          ORDER BY Personnel_id
                                  ,p.[YearWorkingPeriod]
                                  ,[Day]
                                  ,[ShiftType_id]
                        '''.format(work_section_id, year_working_period)

        query_prs__sht_req = '''SELECT [PersonnelTypeReq_id]
                                  ,CAST(SHT.Code AS INT) [ShiftType_id]
                                  ,[ReqMinCount]
                                  ,[ReqMaxCount]
                            FROM 
                                [nip_worksectionrequirements] R
                                JOIN nip_shifttypes SHT ON SHT.ID = R.ShiftType_id
                            WHERE WorkSection_id = {}
                        '''.format(work_section_id)

        db = data(engine=engine,
                  query_gene_last=query_gene_last,
                  query_gene_new=query_gene_new,
                  query_personnel=query_personnel,
                  query_hard_const=query_hard_const,
                  query_shift=query_shift,
                  query_shift_req=query_shift_req,
                  query_prs_req=query_prs_req,
                  query_prs__sht_req=query_prs__sht_req
                  )
        sql_conn = db.get_sql_conn()

        chromosom_df = pd.DataFrame(db.get_chromosom(work_section_id,
                                                     year_working_period, new))
        personnel_df = pd.DataFrame(db.get_personnel())
        hard_const_df = pd.DataFrame(db.get_hard_const())
        shift_df = pd.DataFrame(db.get_shift())
        shifts = np.array(shift_df.reset_index().iloc[:, [0, 4]].values,
                          dtype=int)
        day_req_df = pd.DataFrame(db.get_day_req())
        prs_req_df = pd.DataFrame(db.get_prs_req())
        prs_sht_req_df = pd.DataFrame(db.get_prs__sht_req())

        is_new = db.is_new()
        # ----------------------- gene pivoted ---------------------------------------#
        chromosom_df = chromosom_df.merge(personnel_df,
                                          left_on='Personnel_id',
                                          right_on='Personnel_id',
                                          how='inner')
        chromosom_df = chromosom_df.drop(['WorkSection_id'
                                             , 'YearWorkingPeriod_x'
                                             , 'YearWorkingPeriod_y'
                                          ], axis=1)
        # ----------------------- set personnel_df -----------------------------------#
        prs_sht_req = np.array(prs_sht_req_df.values, dtype=int)
        prs_sht_req = np.concatenate((prs_sht_req,
                                      np.zeros((len(prs_sht_req), 1))),
                                     axis=1)
        prs_sht_req_df.set_index(['PersonnelTypeReq_id', 'ShiftType_id'],
                                 inplace=True)
        # ----------------------- set personnel_df -----------------------------------#
        personnels = np.array(personnel_df.reset_index().iloc[:, [0, 1, 4, 5]].values,
                              dtype=int)
        # ----------------------- set shift_df ---------------------------------------#
        shifts = np.array(shift_df.iloc[:, [0, 3]].values,
                          dtype=int)
        # ----------------------- set day_req_df -------------------------------------#
        day_reqs = np.array(day_req_df.iloc[:, [1, 2, 3]].values,
                            dtype=int)
        day_count = len(day_req_df.groupby(axis=0, level=0, as_index=True).count())
        # -----------------------Randomize gene---------------------------------------#
        if (is_new):
            chromosom_df = pd.pivot_table(chromosom_df, values='Shift_id',
                                          index=['Personnel_id',
                                                 'prs_typ_id',
                                                 'EfficiencyRolePoint',
                                                 'RequirementWorkMins_esti'
                                                 ],
                                          columns=['Day'], aggfunc=np.sum)

            shift_list = np.flip(shifts[:, 0].tolist())
            for prs in chromosom_df.index:
                chromosom_df.loc[prs] = np.random.choice(shift_list,
                                                         # p=[1 / 14, 1 / 14, 1 / 14,
                                                         #    1 / 14, 2 / 14, 3 / 14, 5 / 14],
                                                         size=len(chromosom_df.columns)
                                                         )
        else:
            chromosom_df = chromosom_df.set_index(['Personnel_id',
                                                   'prs_typ_id',
                                                   'EfficiencyRolePoint',
                                                   'RequirementWorkMins_esti'
                                                   ])
            columns={'D01': 1, 'D02': 2, 'D03': 3, 'D04': 4, 'D05': 5, 'D06': 6,
                     'D07': 7, 'D08': 8, 'D09': 9, 'D10': 10, 'D11': 11, 'D12': 12,
                     'D13': 13, 'D14': 14, 'D15': 15, 'D16': 16, 'D17': 17, 'D18': 18,
                     'D19': 19, 'D20': 20, 'D21': 21, 'D22': 22, 'D23': 23, 'D24': 24,
                     'D25': 25, 'D26': 26, 'D27': 27, 'D28': 28, 'D29': 29, 'D30': 30,
                     'D31': 31}
            if PersianMonth>6:
                del columns['D31'] 
                chromosom_df.drop(columns=['D31'], axis=1, inplace=True)
            if PersianMonth==12:
                del columns['D30'] 
                chromosom_df.drop(columns=['D30'], axis=1, inplace=True)
            chromosom_df.rename(columns=columns, inplace=True)
        # ---------------------- calcute typid_req_day--------------------------------#
        req_day = day_req_df.reset_index()
        typid_req_day = req_day.groupby(['Day', 'prs_typ_id', 'shift_type_id']).agg(
            ReqMinCount=pd.NamedAgg(column='ReqMinCount',
                                    aggfunc='sum'),
            ReqMaxCount=pd.NamedAgg(column='ReqMaxCount',
                                    aggfunc='sum')
        )
        typid_req_day['ReqMean'] = (typid_req_day['ReqMaxCount'] +
                                    typid_req_day['ReqMinCount']) / 2
        # ---------------------- Calcute diff require and resource--------------------#
        # ---------------sum_typid_req---------------#
        sum_typid_req = typid_req_day.reset_index()
        sum_typid_req = sum_typid_req.groupby('prs_typ_id').agg(
            req_min=pd.NamedAgg(column='ReqMinCount',
                                aggfunc='sum'),
            req_max=pd.NamedAgg(column='ReqMaxCount',
                                aggfunc='sum'),
            req_mean=pd.NamedAgg(column='ReqMean',
                                 aggfunc='sum'),
        )
        sum_typid_req = sum_typid_req[:] * 480
        # --------------sum_typid_prs----------------#
        sum_typid_prs = personnel_df.groupby('prs_typ_id').agg(
            all_rec=pd.NamedAgg(column='RequirementWorkMins_esti',
                                aggfunc='sum'),
            count_prs=pd.NamedAgg(column='RequirementWorkMins_esti',
                                  aggfunc='count'),
        )
        # --------------sum_typid_prs----------------#
        diff_req_rec = sum_typid_req.join(sum_typid_prs, how='inner')
        diff_req_rec['diff_min'] = (diff_req_rec['req_min'] -
                                    diff_req_rec['all_rec']) / diff_req_rec['count_prs']
        diff_req_rec['diff_max'] = (diff_req_rec['req_max'] -
                                    diff_req_rec['all_rec']) / diff_req_rec['count_prs']
        diff_req_rec['diff_mean'] = (diff_req_rec['req_mean'] -
                                     diff_req_rec['all_rec']) / diff_req_rec['count_prs']
        # diff_req_rec = diff_req_rec.reset_index()

        diff = np.zeros((len(personnels), 3), dtype=int)
        for i, p in enumerate(personnels):
            typ = p[3]
            diff[i, 0] = personnels[i, 2] + diff_req_rec.loc[typ, 'diff_min']
            diff[i, 1] = personnels[i, 2] + diff_req_rec.loc[typ, 'diff_max']
            diff[i, 2] = personnels[i, 2] + diff_req_rec.loc[typ, 'diff_mean']

        personnels = np.append(personnels, diff, 1)

        hard_const_days = list(hard_const_df['Day'])
        hard_const_prs = list(hard_const_df['Personnel_id'])
        hard_const_val = list(hard_const_df['Value'])
        hard_const_sht = list(hard_const_df['ShiftType_id'])
        hard_const = np.ones((len(hard_const_days), 4), dtype=int)
        import math
        for i, d in enumerate(hard_const_days):
            prs = hard_const_prs[i]
            
            hard_const[i, 0] = personnels[personnels[:, 1] == prs][0, 0]
            hard_const[i, 1] = d - 1
            hard_const[i, 2] = 0 if hard_const_sht[i] is None else hard_const_sht[i]
            hard_const[i, 3] = hard_const_val[i]

        # ------------------------ Consttraint day_const function for day -------------#
        def calc_day_const(individual):
            row, col = individual.shape
            diffs_sum = []
            diffs_max = []
            for d in range(col):
                prs_sht_req[:, 4] = 0
                for p in range(row):
                    shift = individual[p, d]
                    prs_typ = personnels[p, 3]
                    typ1 = shift % 10
                    typ2 = shift // 10

                    req1 = np.where((prs_sht_req[:, 0] == prs_typ) &
                                    (prs_sht_req[:, 1] == typ1))
                    prs_sht_req[req1, 4] += 1
                    if typ2:
                        req2 = np.where((prs_sht_req[:, 0] == prs_typ) &
                                        (prs_sht_req[:, 1] == typ2))
                        prs_sht_req[req2, 4] += 1
                diff_min = np.absolute(prs_sht_req[:, 2] - prs_sht_req[:, 4])
                diff_max = np.absolute(prs_sht_req[:, 3] - prs_sht_req[:, 4])
                diff = np.min((diff_min, diff_max), axis=0)
                diffs_sum.append(np.sum(diff))
                diffs_max.append(np.max(diff))

            max_err = len(prs_sht_req) * max(prs_sht_req[:, 2]) * col
            cost = (sum(diffs_sum) + sum(diffs_max)) / (max_err+1)

            return cost

        # ------------------------ Consttraint prs_const function for day -------------#
        def calc_prs_const(ind_length):
            sum_shift = np.sum(ind_length, axis=1)
            diff = np.absolute(sum_shift - personnels[:, 5])
            diff_max = np.max(diff)
            diff_min = np.min(diff)
            diff_range = (diff_max - diff_min) / diff_max

            diff_cost = np.mean(diff / personnels[:, 5])

            cost = diff_cost + diff_range

            return cost

        # ------------------------ Objective prs_req function for prs req -------------#
        def calc_prs_req_cost(ind_length):
            cost = 0

            return cost

        # ------------------------ SET Constraints functions --------------------------#
        def set_hard_const(individual):
            for l in hard_const:
                if l[3]==1: # Shoud not be   
                    if l[2]==0: # All shift type              
                        individual[l[0], l[1]] = 4
                    else:
                        individual[l[0], l[1]] = individual[l[0], l[1]] if individual[l[0], l[1]] != l[2] else 4
                elif l[3]==-1: # Shoud be   
                    if l[2]==0: # All shift type              
                        individual[l[0], l[1]] = l[2] if individual[l[0], l[1]] != 4 else 1
                    else:
                        individual[l[0], l[1]] = l[2]

            return individual

        # ----------------------- fitness all ----------------------------------------#
        def fitness(individual, meta_data):
            individual = set_hard_const(individual)
            ind_length = individual.copy()
            for s in shifts:
                shift = s[0]
                length = s[1]
                ind_length[ind_length == shift] = length

            const_day = coh_day * calc_day_const(individual)
            const_prs = coh_prs * calc_prs_const(ind_length)
            prs_req_cost = calc_prs_req_cost(individual)
            cost = const_day + const_prs
            return cost

        # -----------------------Define GA--------------------------------------------#
        chromosom = np.array(chromosom_df.values, dtype=int)
        ga = GA_numpy.GeneticAlgorithm(seed_data=chromosom,
                                       meta_data=shifts,
                                       population_size=population_size,
                                       generations=generations,
                                       max_const_count=max_const_count,
                                       crossover_probability=crossover_probability,
                                       mutation_probability=mutation_probability,
                                       elitism=True,
                                       by_parent=by_parent,
                                       maximise_fitness=False,
                                       initial_elit_prob=0.5,
                                       initial_random_prob=0.5,
                                       show_plot=show_plot)

        # ----------------------- run ga --------------------------------------------#
        ga.fitness_function = fitness  # set the GA's fitness function
        start_time = time.gmtime()
        ga.run()  # run the GA

        end_time = time.gmtime()
        time_consum_hour = end_time[3] - start_time[3]
        time_consum_minute = end_time[4] - start_time[4]
        time_consum_second = end_time[5] - start_time[5]
        print('time_consum : ' + str(time_consum_hour) + ':' +
              str(time_consum_minute) + ':' +
              str(time_consum_second)
              )
        sol_fitness, sol = ga.best_individual()

        sol_df = chromosom_df.copy()
        working_period = year_working_period%100
        
        days = range(len(sol_df.columns)) 
            
        for day in days:
            sol_df[day + 1] = sol[:, day]

        sol_tbl = sol_df.stack()
        sol_tbl = sol_tbl.reset_index()

        Rank = 1
        Cost = sol_fitness
        EndTime = int(round(time.time() * 1000))
        UsedParentCount = 0
        present_id = self.present_id
        #
        # sol_tbl = sol_tbl.drop(columns=['prs_typ_id',
        #                                'EfficiencyRolePoint',
        #                                'RequirementWorkMins_esti'])
        # sol_tbl = sol_tbl.astype(int)
        # sol_tbl = sol_tbl.values.tolist()

        # ----------------------- inserting ------------------------------------------#

        ShiftAssignment_id = db.insert_sol(sol_df, personnel_df,
                                           sol_fitness, work_section_id,
                                           year_working_period, year_working_period_value,
                                           parent_rank,
                                           Rank, Cost, EndTime, UsedParentCount,
                                           present_id, rec_id
                                           )

        db.update_sps(work_section_id, year_working_period, parent_rank)
        # -------------------- output show --------------------------------------------#
        ########################################################
        sht = shift_df.reset_index()
        sht_2 = sht[sht['ShiftCode'] > 10]
        sht_2['Length'] = sht_2['Length'] // 2
        sht_2['shift_type_id'] = sht_2['shift_type_id'] // 10
        sht_2.index = [7, 8, 9]
        sht_len = sht[sht['ShiftCode'] > 10]['Length'] // 2
        sht.update(sht_len)
        sht['shift_type_id'] = sht['shift_type_id'] % 10
        sht = sht.append(sht_2)
        df = pd.melt(sol_df.reset_index(),
                     id_vars=['Personnel_id',
                              'prs_typ_id',
                              'EfficiencyRolePoint',
                              'RequirementWorkMins_esti',

                              ],
                     var_name='Day',
                     value_name='Shift_id')
        df = df.merge(sht, left_on='Shift_id', right_on='Shift_id', how='inner')
        #########################################################
        cons_prs = df.groupby(['Personnel_id',
                               'prs_typ_id',
                               'EfficiencyRolePoint',
                               'RequirementWorkMins_esti',

                               ]).sum().drop(columns=['Shift_id',
                                                      'StartTime',
                                                      'EndTime',
                                                      'shift_type_id'])

        cons_prs = cons_prs.reset_index(level=3)
        cons_prs['ExtraForce'] = personnels[:, 6]
        cons_prs['diff'] = (cons_prs['Length'] - personnels[:, 6])
        #########################################################
        cons_day = df[df['Length'] > 0].groupby(['Day',
                                                 'prs_typ_id',
                                                 'shift_type_id']).agg(
            prs_count=pd.NamedAgg(column='Length',
                                  aggfunc='count'),
            prs_points=pd.NamedAgg(column='EfficiencyRolePoint',
                                   aggfunc='sum'),
        )

        cons_day = cons_day.join(typid_req_day,
                                 how='right')

        cons_day.fillna(0, inplace=True)

        cons_day['diff_max'] = abs(cons_day['prs_count'] - cons_day['ReqMaxCount'])
        cons_day['diff_min'] = abs(cons_day['prs_count'] - cons_day['ReqMinCount'])
        cons_day['diff'] = cons_day[['diff_max', 'diff_min']].apply(np.min, axis=1)
        cons_day.sort_index(axis=0, level=[0, 1, 2], ascending=True, inplace=True)

        db.insert_cons_day(ShiftAssignment_id, cons_day)
        db.insert_cons_prs(ShiftAssignment_id, cons_prs)

        return present_id
