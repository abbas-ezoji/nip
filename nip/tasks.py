from celery.decorators import task
import sys
sys.path.insert(0, "D:\\nip_project\\nip\\training")

from .training import utils


@task(name="set_shift")
def set_shift_async(work_sction_id, year_working_period, coh_day, coh_prs,
                    population_size, generations, max_const_count, crossover_probability,
                    mutation_probability, elitism, show_plot, by_parent, new):
    
    sh = utils.shift(work_sction_id=work_sction_id,
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

    return present_id
