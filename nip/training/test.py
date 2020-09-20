import sys
sys.path.insert(0, "D:\\nip_project\\nip\\training")

from training import utils

WorkSection=1
YearWorkingPeriod=139806
coh_const_DayRequirements=0.999
coh_const_PersonnelPerformanceTime=0.001
TaskStatus=1
RecommenderStatus=0
PopulationSize=80
GenerationCount=500
MaxFitConstRate=0.3
CrossoverProbability=0.2
MutationProbability=0.8
# DevByParent=on

sh = utils.shift(work_sction_id = 1,
                year_working_period = 139806,
                coh_day = 0.999,            # coh for day requirements const
                coh_prs = 0.001,            # coh for personnel times
                population_size = 80,
                generations = 200,
                max_const_count = 0.3,
                crossover_probability = 0.2,
                mutation_probability = 0.8,
                elitism = False,
                show_plot = True,
                by_parent = True,
                new = 0)
present_id = sh.set_shift()