# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
import pandas as pd
import pyodbc

class data(object): 
    def __init__(self, 
                 engine, 
                 query_gene_last,
                 query_gene_new,
                 query_personnel,
                 query_leaves,
                 query_shift,
                 query_shift_req,
                 query_prs_req,
                 query_prs__sht_req
                 ):
        # -------------------- Connection String -----------------------------#
        self.engine = engine
        # ------------------ Query for gene pivoted --------------------------#
        self.query_gene_last = query_gene_last
        self.query_gene_new = query_gene_new
        # ----------------- Query for personnel info -------------------------#
        self.query_personnel = query_personnel   
        self.query_leaves = query_leaves
        # -------------------Query for shift info-----------------------------#
        self.query_shift = query_shift  
        # -------------------Query for shift_req info-------------------------#
        self.query_shift_req = query_shift_req 
        # -------------------Query for shift_req info-------------------------#
        self.query_prs_req = query_prs_req 
        # -------------------Query for shift_req info-------------------------#
        self.query_prs__sht_req = query_prs__sht_req 
        #---------------------------------------------------------------------#         
        
        self.new = 0
               
    def get_sql_conn(self):
        engine = self.engine
        return engine
        
    def get_chromosom(self, work_sction_id, year_working_period, new):  
        q = self.query_gene_last
        chromosom_df = pd.read_sql(self.query_gene_last, self.engine)
        if(chromosom_df.empty or new):              
            self.new = 1
            chromosom_df = pd.read_sql(self.query_gene_new, self.engine)        
            
        return chromosom_df
    
    def get_personnel(self):
        personnel_df = pd.read_sql(self.query_personnel,self.engine)    
        return personnel_df
    
    def get_leaves(self):
        leaves_df = pd.read_sql(self.query_leaves,self.engine)    
        return leaves_df
    
    def get_shift(self):
        shift_df = pd.read_sql(self.query_shift,self.engine)
        return shift_df
    
    def get_day_req(self):
        day_req_df = pd.read_sql(self.query_shift_req,self.engine)
        return day_req_df
    
    def get_prs_req(self):
        query_prs_req = pd.read_sql(self.query_prs_req,self.engine)
        return query_prs_req
    
    def get_prs__sht_req(self):
        query_prs__sht_req = pd.read_sql(self.query_prs__sht_req,self.engine)
        return query_prs__sht_req
        
    def delete_last_sol(self,work_sction_id,year_working_period):        
        query_delete = '''delete from nip_PersonnelShiftDateAssignments 
                          where WorkSection_Id ={0} and YearWorkingPeriod = {1}
                        '''.format(work_sction_id,year_working_period)
        with self.engine.connect() as con:
            con.execute(query_delete)
                             
    def is_new(self):
        return self.new
    
    def update_sps(self, work_sction_id, year_working_period, parent_rank):
        #---------------- update UsedParentCount of parent solution ----------#
        sp_parent = '''exec [dbo].[UpdateUsedParentCount] {0}, {1}, {2}
                           '''.format(work_sction_id,year_working_period, parent_rank)
        self.engine.execute(sp_parent)            
        #---------------- update Rank of last solutions ----------------------#
        sp_rank = '''exec [dbo].[UpdateLastRanks] {0}, {1}                         
                           '''.format(work_sction_id,year_working_period)
        self.engine.execute(sp_rank)  
        
    def insert_sol(self, sol_df, personnel_df, sol_fitness,
                   work_sction_id,year_working_period,
                   parent_rank,Rank, Cost, EndTime, UsedParentCount, present_id):                  
        
        sol_df = sol_df.reset_index()
        sol_df = sol_df.drop(columns=['prs_typ_id', 'EfficiencyRolePoint', 
                                      'RequirementWorkMins_esti'])
        with self.engine.connect() as con:
            con.execute('''insert into [nip_shiftassignments] 
                               ([YearWorkingPeriod]
                              ,[Rank]
                              ,[Cost]
                              ,[EndTime]
                              ,[UsedParentCount]
                              ,[WorkSection_id]
                              ,[present_id])
                               values (?, ?, ?, ?, ?, ?, ?)'''
                               ,(year_working_period, Rank, Cost,
                                 EndTime, UsedParentCount, 
                                 work_sction_id,present_id)
                               ) 
                               
            inserted_shift = pd.read_sql_query('''SELECT * 
                                                    FROM nip_shiftassignments
                                                    WHERE present_id = {0} 
                                                    '''.format( "'"+str(present_id)+"'")
                                                , self.engine)
            ShiftAssignment_id = int(inserted_shift['id'])
        #------------------------ insert new solution ------------------------#
            
            for index, t in sol_df.iterrows():                
                insert_qry = '''insert into nip_PersonnelShiftDateAssignments 
                                   ([Personnel_id]                                  
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
                                  ,[ShiftAssignment_id]
                                  ,[YearWorkingPeriod])
            values ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
                    {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
                    {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
                    {})'''.format(t['Personnel_id'], 
                                  t[1], t[3], t[3], t[4], t[5],
                                  t[6], t[7], t[8], t[9], t[10], t[11],
                                  t[12], t[14], t[14], t[15], t[16], t[17],
                                  t[18], t[19], t[20], t[21], t[22], t[23],
                                  t[24], t[25], t[26], t[27], t[28], t[29],
                                  t[30], t[31],
                                  ShiftAssignment_id,
                                  year_working_period
                                  )
                con.execute(insert_qry)  
    
        return ShiftAssignment_id
        
    def insert_cons_day(self, ShiftAssignment_id, cons_day):
        cons_day.reset_index(inplace=True)
        
        with self.engine.connect() as con:
            for index, t in cons_day.iterrows():   
                con.execute('''insert into [nip_shiftconstdayrequirements]
                                       ([Day]
                                      ,[PersonnelTypes_id] 
                                      ,[ShiftTypes_id]                                                                                     
                                      ,[PersonnelCount]
                                      ,[PersonnelPoints]
                                      ,[RequireMinCount]
                                      ,[RequireMaxCount]
                                      ,[RequireMeanCount]
                                      ,[DiffMinCount]
                                      ,[DiffMaxCount]
                                      ,[DiffCount]
                                      ,[ShiftAssignment_id])                           
                                       values ({}, {}, {}, {}, {}, {},
                                               {}, {}, {}, {}, {}, 
                                               {})
                                       '''.format(t[0],t[1], t[2], t[3], t[4], t[5],
                                                  t[6],t[7], t[8], t[9], t[10], 
                                                  ShiftAssignment_id)
                                                   ) 
    
    def insert_cons_prs(self, ShiftAssignment_id, cons_prs):
        cons_prs.reset_index(inplace=True)
        cons_prs = cons_prs.drop(columns=['index', 'ShiftCode'])
        with self.engine.connect() as con:
            for index, t in cons_prs.iterrows():   
                con.execute('''insert into [nip_shiftconstpersonneltimes]
                                               ([Personnel_id]
                                              ,[PersonnelTypes_id]
                                              ,[EfficiencyRolePoint]
                                              ,[RequireMinsEstimate]
                                              ,[AssignedTimes]
                                              ,[ExtraForce]
                                              ,[Diff]                                                                          
                                              ,[ShiftAssignment_id])                           
                                               values ({}, {}, {}, {}, 
                                                       {}, {}, {}, {})
                                               '''.format(t[0],t[1], t[2], 
                                                           t[3], t[4], t[5], t[6],                                              
                                                          ShiftAssignment_id)
                                                           ) 
# =============================================================================
        # self.update_sps(work_sction_id, year_working_period, parent_rank)
#          
# =============================================================================
    