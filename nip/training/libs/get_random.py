# -*- coding: utf-8 -*-
import random

colt2 = (random.randrange(29, 31 ))

import copy
import pyodbc
import pandas as pd
import numpy as np
import time

def RouletteWheelSelection(P):
        r=random.random()
        C=np.cumsum(P)
        
        try:    
            j=np.where(C>=r)[0][0]  #find(r<=C,1,'first');
        except:
            j=0
        
        return j   

def get_rollet_wheel(prob_list, rank_list):
    cd_prob = copy.deepcopy(prob_list)
    p = random.random()
    for i in range(len(rank_list)):        
        cd_prob[i] =  sum(prob_list[:i+1]) if prob_list[i] else 0    
    
    r = -1    
    for i in range(len(cd_prob)):    
        if p < cd_prob[i]:
            r = rank_list[i]
            break
    return r

def get_best_first_rank(engine, query_gene_last):    
           
    last_df = pd.read_sql(query_gene_last, engine)
    if last_df.empty:
        return 0
    t = int(round(time.time() * 1000))
    last_df['life_cycle'] = t -last_df['EndTime']
    min_diff = min(last_df['life_cycle'])
    last_df['life_cycle'] = last_df['life_cycle'] / min_diff
    
    last_df['point'] = ( last_df['life_cycle']
                          / 
                         (last_df['Rank'] * 
                          last_df['Cost'] * 
                          (last_df['UsedParentCount'] + 1 )                      
                         )
                        )
    sum_point = sum(last_df['point'])
    last_df['point'] = last_df['point'] / sum_point
    rank_list = last_df['Rank']
    prob_list = last_df['point']
    
    j=RouletteWheelSelection(prob_list)
    
    return j+1


