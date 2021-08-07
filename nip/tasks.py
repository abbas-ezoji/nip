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


@task(bind=True, name="ETL")
def ETL_async(self, YearWorkingPeriod):
    logger.info(f"ETL run for YearWorkingPeriod={YearWorkingPeriod}")
    try:
        logger.info("Start:")
        q = etl.ETL(YearWorkingPeriod)
    except Exception as e:
        logger.error(e)
        q = ''

    return q


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
def set_shift_async(self, work_section_id, year_working_period, year_working_period_value, coh_day, coh_prs,
                    population_size, generations, max_const_count, crossover_probability,
                    mutation_probability, elitism, show_plot, by_parent, new, rec_id):
    print(year_working_period_value, year_working_period)
    sh = utils.shift(work_section_id=work_section_id,
                     year_working_period=year_working_period,
                     year_working_period_value=year_working_period_value,
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
                     new=new,
                     rec_id=rec_id)

    present_id = sh.get_present_id()
    logger.info(f"rec_id: {rec_id}, present_id={present_id}, WorkSection={work_section_id}, YearWorkingPeriod={year_working_period}")
    try:
        logger.info("Start:")
        sh.set_shift()
    except Exception as e:
        print('errrrrrror:'+ str(year_working_period_value))
        logger.error(e)

    return present_id


@task(bind=True, name="get_hospital")
def get_hospital_async(self, PersonnelBaseId, Date, ShiftGuid):
    logger.info(f"PersonnelBaseId={PersonnelBaseId}, Date={Date}, ShiftGuid={ShiftGuid}")
    try:
        logger.info("Start:")
        q = etl.update_shift(PersonnelBaseId=PersonnelBaseId, Date=Date, ShiftGuid=ShiftGuid)
    except Exception as e:
        logger.error(e)
        q = ''

    return q
