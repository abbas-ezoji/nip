from training import utils

work_section_id=44008
year_working_period=139909
coh_day=0.99
coh_prs=0.001
population_size=80
generations=5
max_const_count=20
crossover_probability=0.8
mutation_probability=0.2
elitism=False,
show_plot=False,
by_parent=True,
new=True

sh = utils.shift(work_section_id=work_section_id,
                     year_working_period=year_working_period,
                     coh_day=coh_day,
                     coh_prs=coh_prs,
                     population_size=population_size,
                     generations=generations,
                     max_const_count=max_const_count,
                     crossover_probability=crossover_probability,
                     mutation_probability=mutation_probability,
                     elitism=True,
                     show_plot=show_plot,
                     by_parent=True,
                     new=new)
present_id = sh.get_present_id()

sh.set_shift()