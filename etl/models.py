from django.db import models
from nip.tasks import ETL_async


class ETL(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    YearWorkingPeriod = models.IntegerField('سال-دوره', db_column='YearWorkingPeriod')
    HospitalDepartmentCode = models.IntegerField('کد بیمارستان', db_column='HospitalDepartmentCode')

    def __str__(self):
        return str(self.YearWorkingPeriod)

    class Meta:
        verbose_name = 'فرایند استخراج داده'
        verbose_name_plural = 'فرایند استخراج داده'
        db_table = 'nip_ETL'

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)

        ETL_async.delay(self.YearWorkingPeriod)

        super(ETL, self).save(*args, **kwargs)

