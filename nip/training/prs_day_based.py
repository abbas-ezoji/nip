'''
            <<<<Shift Recommandeation by Genetic Algorithm>>>>            
    - Create initial gene by pivot table
    - Fetch Personnel, Shift and WorkSection Requirements Info
'''
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

population_size=80
generations=500
max_const_count=0.2
crossover_probability=0.2
mutation_probability=0.8
elitism=False
show_plot=True

by_parent = True
new = False
#-------------------------------------------------------
PersianYear  = int(year_working_period / 100)
PersianMonth = int(year_working_period % 100)
# ----------------------- get data -------------------------------------------#
USER = 'sa' # settings.DATABASES['default']['USER']
PASSWORD = '1qaz!QAZ' # settings.DATABASES['default']['PASSWORD']
HOST = '172.16.47.154' # settings.DATABASES['default']['HOST']
PORT = '1433' # settings.DATABASES['default']['PORT']
NAME = 'nip' # settings.DATABASES['default']['NAME']

engine = create_engine('mssql+pyodbc://{}:{}@{}/{}?driver=SQL+Server' \
                       .format(USER,
                               PASSWORD,
                               HOST,                    
                               NAME
                               ))              
              
query_gene_last = '''SELECT DISTINCT   

                            [Rank]
                           ,[Cost]      
                           ,[WorkSection_id]
                           ,[YearWorkingPeriod]
                           ,[EndTime]
                           ,0 life_cycle	 
                           ,[UsedParentCount]
                     FROM [nip_shiftassignments]                         
                     WHERE WorkSection_id = {0} AND YearWorkingPeriod = {1}                                
                   '''.format(work_sction_id,year_working_period) 
                       
parent_rank = get_rank(engine, query_gene_last)

query_gene_last ='''SELECT st.[Personnel_id]
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
                 '''.format(work_sction_id,
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
                  '''.format(PersianYear, PersianMonth, work_sction_id)                  

query_personnel = '''SELECT  id [Personnel_id]
							,[WorkSection_id]
							,[YearWorkingPeriod]
							,[RequirementWorkMins_esti]
							,[RequirementWorkMins_real]
							,[PersonnelTypes_id] prs_typ_id
							,[EfficiencyRolePoint]
                            ,[DiffNorm]
                    FROM [nip_Personnel]
                    WHERE WorkSection_id = {0} AND YearWorkingPeriod = {1}
                  '''.format(work_sction_id,year_working_period)

query_leaves = '''SELECT P.[YearWorkingPeriod]
                      ,[Day]      
                      ,[Personnel_id]
                  FROM [nip_personnelleaves] l join 
                	 [nip_personnel] p on p.id=l.Personnel_id
                  WHERE P.WorkSection_id = {} AND P.YearWorkingPeriod = {}
                  '''.format(work_sction_id,year_working_period)
                  
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
                          ,[ShiftType_id] shift_type_id
                          ,[ReqMinCount]
                          ,[ReqMaxCount]
                          ,[day_diff_typ]
                    FROM 
                    	[nip_WorkSectionRequirements] R
                    	JOIN nip_dim_date D ON D.PersianYear=R.Year
                    	AND D.PersianMonth = R.Month                    	
                    WHERE 
						YEAR = {} AND Month = {}
                        AND WorkSection_id = {}
                    ORDER BY 
                    	WorkSection_id,D.PersianDate
                    	,PersonnelTypeReq_id,ShiftType_id                        
                                          
                  '''.format(PersianYear, PersianMonth, work_sction_id)      
query_prs_req = '''SELECT  [Personnel_id] 
                          ,p.[YearWorkingPeriod]
                          ,p.[WorkSection_id]
                          ,[Day]
                          ,[ShiftType_id] as shift_type_id
                          ,[Value]
                  FROM [nip_personnelrequest] r join [nip_personnel] p
					   on p.id = r.Personnel_id
                  WHERE p.[WorkSection_id] = {0}
                        and p.[YearWorkingPeriod] = {1}
                  ORDER BY Personnel_id
                          ,p.[YearWorkingPeriod]
                          ,[Day]
                          ,[ShiftType_id]
                '''.format(work_sction_id,year_working_period)
                     
db = data(engine =  engine,
          query_gene_last = query_gene_last,
          query_gene_new = query_gene_new,
          query_personnel=query_personnel,
          query_leaves=query_leaves,
          query_shift=query_shift,
          query_shift_req=query_shift_req,
          query_prs_req=query_prs_req
         )
sql_conn = db.get_sql_conn()

chromosom_df = pd.DataFrame(db.get_chromosom(work_sction_id, 
                                             year_working_period, new))
personnel_df = pd.DataFrame(db.get_personnel())
leaves_df = pd.DataFrame(db.get_leaves())
shift_df = pd.DataFrame(db.get_shift())
day_req_df = pd.DataFrame(db.get_day_req())
prs_req_df = pd.DataFrame(db.get_prs_req())
is_new = db.is_new()
# ----------------------- gene pivoted ---------------------------------------#
chromosom_df = chromosom_df.merge(personnel_df, 
                                  left_on='Personnel_id', 
                                  right_on='Personnel_id', 
                                  how='inner')
chromosom_df = chromosom_df.drop(['WorkSection_id'
                                 ,'YearWorkingPeriod_x'
                                 ,'YearWorkingPeriod_y'                                
                                 ,'RequirementWorkMins_real'
                                 ,'DiffNorm'], axis=1)

# ----------------------- set personnel_df -----------------------------------#
personnel_df = personnel_df.set_index('Personnel_id')
personnel_df['DiffNorm'] = 0
# ----------------------- set shift_df ---------------------------------------#
shift_df = shift_df.set_index('Shift_id')
# ----------------------- set day_req_df -------------------------------------#
day_req_df = day_req_df.set_index(['Day','prs_typ_id','shift_type_id'])
day_req_df['day_diff_typ'] = 0
day_count =len(day_req_df.groupby(axis=0, level=0, as_index=True).count())
# -----------------------Randomize gene---------------------------------------#
if (is_new):  
    chromosom_df = pd.pivot_table(chromosom_df, values='Shift_id', 
                              index=['Personnel_id',
                                      'prs_typ_id',
                                      'EfficiencyRolePoint',
                                      'RequirementWorkMins_esti'                                                                           
                                    ],
                              columns=['Day'], aggfunc=np.sum)    
    
    shift_list = np.flip(shift_df.index.values.tolist())   
    for prs in chromosom_df.index :       
        chromosom_df.loc[prs] = np.random.choice(shift_list,
                                                 p=[1/14,1/14,1/14,
                                                    1/14,2/14,3/14,5/14],
                                                 size=len(chromosom_df.columns)
                                                 )    
else:
    chromosom_df = chromosom_df.set_index(['Personnel_id',
                                          'prs_typ_id',
                                          'EfficiencyRolePoint',
                                          'RequirementWorkMins_esti'                                                                           
                                        ])
    chromosom_df.rename(
            columns={'D01':1,'D02':2,'D03':3,'D04':4,'D05':5,'D06':6,
                     'D07':7,'D08':8,'D09':9,'D10':10,'D11':11,'D12':12,
                     'D13':13,'D14':14,'D15':15,'D16':16,'D17':17,'D18':18,
                     'D19':19,'D20':20,'D21':21,'D22':22,'D23':23,'D24':24,
                     'D25':25,'D26':26,'D27':27,'D28':28,'D29':29,'D30':30,
                     'D31':31}, 
                 inplace=True)
# ---------------------- calcute typid_req_day--------------------------------#
req_day = day_req_df.reset_index()
typid_req_day = req_day.groupby(['Day','prs_typ_id','shift_type_id']).agg(
                ReqMinCount = pd.NamedAgg(column='ReqMinCount', 
                                          aggfunc='sum'),
                ReqMaxCount = pd.NamedAgg(column='ReqMaxCount', 
                                          aggfunc='sum')
                )
typid_req_day['ReqMean'] = (typid_req_day['ReqMaxCount']+ 
                            typid_req_day['ReqMinCount'])/2   
# ---------------------- Calcute diff require and resource--------------------# 
                    #---------------sum_typid_req---------------#
sum_typid_req = typid_req_day.reset_index()          
sum_typid_req = sum_typid_req.groupby('prs_typ_id').agg(
            req_min  = pd.NamedAgg(column='ReqMinCount', 
                                          aggfunc='sum'), 
            req_max = pd.NamedAgg(column='ReqMaxCount', 
                                          aggfunc='sum'),
            req_mean= pd.NamedAgg(column='ReqMean', 
                                          aggfunc='sum'),            
        )
sum_typid_req = sum_typid_req[:]*480
                     #--------------sum_typid_prs----------------#
sum_typid_prs = personnel_df.groupby('prs_typ_id').agg(
            all_rec  = pd.NamedAgg(column='RequirementWorkMins_esti', 
                                          aggfunc='sum'), 
            count_prs = pd.NamedAgg(column='RequirementWorkMins_esti', 
                                          aggfunc='count'),
        )
                     #--------------sum_typid_prs----------------#
diff_req_rec = sum_typid_req.join(sum_typid_prs,how='inner')                   
diff_req_rec['diff_min'] = (diff_req_rec['req_min'] - 
                            diff_req_rec['all_rec'] )/diff_req_rec['count_prs'] 
diff_req_rec['diff_max'] = (diff_req_rec['req_max'] - 
                            diff_req_rec['all_rec'] )/diff_req_rec['count_prs'] 
diff_req_rec['diff_mean'] = (diff_req_rec['req_mean'] - 
                            diff_req_rec['all_rec'] )/diff_req_rec['count_prs']
#diff_req_rec = diff_req_rec.reset_index()
#------------------------ Consttraint day_const function for day -------------# 
def calc_day_const(individual,meta_data):  
    df = individual           
    df = df[df['Length']>0].groupby(['Day',
                                     'prs_typ_id',
                                     'shift_type_id']).agg(
                        prs_count = pd.NamedAgg(column='Length', 
                                          aggfunc='count'), 
                        prs_points = pd.NamedAgg(column='EfficiencyRolePoint', 
                                          aggfunc='sum'),
                        )
#    df = df.reset_index()
#    meta_data_df = meta_data.reset_index()
    df = df.join(meta_data, how='right') 
    df.fillna(0,inplace=True)
    df['diff_max'] = abs(df['prs_count'] - df['ReqMaxCount'])
    df['diff_min'] = abs(df['prs_count'] - df['ReqMinCount'])  
    df['diff'] = df[['diff_max','diff_min']].apply(np.min, axis=1)
    df['diff_norm'] = df['diff']/df['ReqMaxCount']
#    cost = np.mean(df['diff_norm'])
    df['diff_norm'] = df['diff_norm']**2
    cost = np.sum(df['diff_norm']) / len(df)
#    cost = np.max(df['diff_norm']) / len(df)
#    print('cost: ' + str(cost))
    return cost

#------------------------ Consttraint prs_const function for day -------------# 
def calc_prs_const (individual, meta_data):
    df = individual    
    df = df.groupby(['Personnel_id',
                      'prs_typ_id',
                      'EfficiencyRolePoint',
                      'RequirementWorkMins_esti',                      
                     ]).sum().drop(columns=['Shift_id', 'StartTime', 
                                            'EndTime', 'shift_type_id'])    
    df = df.reset_index()
    meta_data = meta_data.reset_index()
    df = df.merge(meta_data, left_on='prs_typ_id', right_on='prs_typ_id'
                  ,how='inner')
    
    df['diff'] = abs(df['RequirementWorkMins_esti'] + 
                     df['diff_min'] - df['Length'])         
    df['diff_norm'] = df['diff']/df['RequirementWorkMins_esti']
#    cost = np.mean(df['diff_norm'])    
    df['diff_norm'] = df['diff_norm']**2
    cost = np.sum(df['diff_norm']) / len(df)
#    print('cost: ' + str(cost))
    return cost 
#------------------------ Objective prs_req function for prs req -------------# 
def calc_prs_req_cost (individual,meta_data):  
    df = individual     
    df['Assigned'] = 1
    df_req = meta_data.merge(df,  
                             left_on =['Personnel_id','Day','shift_type_id'],
                             right_on=['Personnel_id','Day','shift_type_id'],
                             how='left'
                            )
    df_req = df_req.fillna(-1)
    
    df_req['cost'] = df_req['Assigned']*df_req['Value']

    return 0
#------------------------ SET Constraints functions --------------------------#
def set_off_force(individual):  
    df = individual   
    days = leaves_df['Day']
    personnels = leaves_df['Personnel_id']
    df.reset_index(inplace=True)
    df.set_index('Personnel_id', inplace=True)
    df.loc[personnels, days] = 4

    return df
# ----------------------- fitness all ----------------------------------------#
def fitness (individual, meta_data):
    individual_df = individual
    # individual_df = chromosom_df.copy()
    # days = range(31)
    # for day in days:
    #     individual_df[day+1] = individual[:,day]
        
    individual_df = set_off_force(individual_df)
    sht = shift_df.reset_index()
    sht_2 = sht[sht['ShiftCode']>10]
    sht_2['Length'] = sht_2['Length'] // 2
    sht_2['shift_type_id'] = sht_2['shift_type_id'] // 10
    sht_2.index = [7,8,9]
    sht_len = sht[sht['ShiftCode']>10]['Length'] // 2
    sht.update(sht_len)
    sht['shift_type_id'] = sht['shift_type_id'] % 10
    sht = sht.append(sht_2)
    #sht[sht['ShiftCode']>10]
    df = pd.melt(individual_df.reset_index(), 
                  id_vars=['Personnel_id',
                          'prs_typ_id',
                          'EfficiencyRolePoint',
                          'RequirementWorkMins_esti',                          
                          ],
                  var_name='Day', 
                  value_name='Shift_id')
    df = df.merge(sht, left_on='Shift_id', right_on='Shift_id', how='inner')
    day_const = 0.8*calc_day_const(df, typid_req_day)
    prs_const = 0.2*calc_prs_const(df, diff_req_rec)
    prs_req_cost = calc_prs_req_cost(df, prs_req_df)
    cost = day_const + prs_const
    return cost
# -----------------------Define GA--------------------------------------------#        
chromosom = np.array(chromosom_df.values, dtype=int)
ga = GA_numpy.GeneticAlgorithm( seed_data=chromosom,
                              meta_data=shift_df,
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
ga.fitness_function = fitness         # set the GA's fitness function
start_time = time.gmtime()
ga.run()                                    # run the GA

end_time =  time.gmtime()
time_consum_hour   = end_time[3] - start_time[3]
time_consum_minute = end_time[4] - start_time[4]
time_consum_second = end_time[5] - start_time[5]
print('time_consum : ' + str(time_consum_hour) + ':'+ 
                         str(time_consum_minute) + ':'+ 
                         str(time_consum_second)
                        )
sol_fitness, sol_df = ga.best_individual()

last_pops = ga.last_generation()

sol_tbl = sol_df.stack()
sol_tbl = sol_tbl.reset_index()

Rank = 1
Cost = sol_fitness
EndTime =  int(round(time.time() * 1000))
UsedParentCount =  0
present_id = (str(work_sction_id)+'-'+str(year_working_period)+
                '-'+str(int(round(time.time() * 1000))))
#
#sol_tbl = sol_tbl.drop(columns=['prs_typ_id', 
#                                'EfficiencyRolePoint', 
#                                'RequirementWorkMins_esti'])
#sol_tbl = sol_tbl.astype(int)    
#sol_tbl = sol_tbl.values.tolist()

# ----------------------- inserting ------------------------------------------# 

db.insert_sol(sol_df, personnel_df, 
              sol_fitness,work_sction_id,year_working_period,
              parent_rank,Rank, Cost, EndTime, UsedParentCount, present_id
              )

#db.update_sps(work_sction_id, year_working_period, parent_rank)
#-------------------- output show --------------------------------------------#
########################################################
sht = shift_df.reset_index()
sht_2 = sht[sht['ShiftCode']>10]
sht_2['Length'] = sht_2['Length'] // 2
sht_2['shift_type_id'] = sht_2['shift_type_id'] // 10
sht_2.index = [7,8,9]
sht_len = sht[sht['ShiftCode']>10]['Length'] // 2
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
                      
                     ]).sum().drop(columns=['Shift_id', 'StartTime', 
                                            'EndTime', 'shift_type_id'])
cons_prs = cons_prs.reset_index(level=3)
cons_prs['diff'] = (cons_prs['Length'] - cons_prs['RequirementWorkMins_esti'])//60
#########################################################
cons_day = df[df['Length']>0].groupby(['Day',
                                       'prs_typ_id',
                                       'shift_type_id']).agg(
                              prs_count = pd.NamedAgg(column='Length', 
                                          aggfunc='count'), 
                              prs_points = pd.NamedAgg(column='EfficiencyRolePoint', 
                                          aggfunc='sum'),
                            )
                              
cons_day = cons_day.join(typid_req_day,
                          how='right') 

cons_day.fillna(0,inplace=True)   
cons_day['diff_max'] = abs(cons_day['prs_count'] - cons_day['ReqMaxCount'])
cons_day['diff_min'] = abs(cons_day['prs_count'] - cons_day['ReqMinCount'])  
cons_day['diff'] = cons_day[['diff_max','diff_min']].apply(np.min, axis=1) 
cons_day.sort_index(axis=0, level=[0,1,2], ascending=True, inplace=True)
