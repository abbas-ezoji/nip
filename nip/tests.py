from training import *


def set_shift_async(work_sction_id, year_working_period):
    sh = utils.shift(work_sction_id=work_sction_id,
                     year_working_period=year_working_period)
    sh.set_shift()

    return 1

