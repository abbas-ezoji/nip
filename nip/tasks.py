from __future__ import absolute_import, unicode_literals

import sys

# sys.path.insert(0, "D:\\nip_project\\nip\\training")
from nip.training import etl, utils
from celery import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@task(bind=True, name="test")
def test(self, a, b):
    return a + b


@task(bind=True, name="update_shift")
def update_shift_async(self, PersonnelBaseId, Date, ShiftGuid):
    logger.info(f"PersonnelBaseId={PersonnelBaseId}, Date={Date}, ShiftGuid={ShiftGuid}")
    try:
        logger.info("Start:")
        q = etl.update_shift(PersonnelBaseId=PersonnelBaseId, Date=Date, ShiftGuid=ShiftGuid)
    except Exception as e:
        logger.error(e)
        q = ''

    return q


@task(bind=True, name="set_shift")
def set_shift_async(self, work_section_id, year_working_period, coh_day, coh_prs,
                    population_size, generations, max_const_count, crossover_probability,
                    mutation_probability, elitism, show_plot, by_parent, new):
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
    logger.info(f"present_id={present_id}, WorkSection={work_section_id}, YearWorkingPeriod={year_working_period}")
    try:
        logger.info("Start:")
        sh.set_shift()
    except Exception as e:
        logger.error(e)

    return present_id
