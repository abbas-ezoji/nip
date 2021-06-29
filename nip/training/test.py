import sys
sys.path.insert(0, "D:\\nip_project\\nip\\training")

from training import utils

WorkSection=45234
YearWorkingPeriod=1016
YearWorkingPeriod_value=140004
coh_const_DayRequirements=0.999
coh_const_PersonnelPerformanceTime=0.001
TaskStatus=1
RecommenderStatus=0
PopulationSize=100
GenerationCount=500
MaxFitConstRate=0.3
CrossoverProbability=0.2
MutationProbability=0.8
new = 0
# DevByParent=on

sh = utils.shift(work_section_id = WorkSection,
                year_working_period = YearWorkingPeriod,
                year_working_period_value = YearWorkingPeriod_value,
                coh_day =coh_const_DayRequirements,
                coh_prs = coh_const_PersonnelPerformanceTime,
                population_size = PopulationSize,
                generations = GenerationCount,
                max_const_count = MaxFitConstRate,
                crossover_probability = CrossoverProbability,
                mutation_probability = MutationProbability,
                elitism = False,
                show_plot = True,
                by_parent = True,
                new = new)
ppp = sh.get_present_id()

present_id = sh.set_shift()