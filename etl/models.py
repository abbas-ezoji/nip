from django.db import models
from nip.tasks import ETL_async

States = (
    (0, ("غیرفعال")),
    (1, ("فعال")),
)


class YearWorkingPeriod(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    YearWorkingPeriod = models.IntegerField('سال-دوره', db_column='YearWorkingPeriod')
    State = models.IntegerField('وضعیت', db_column='State', choices=States, default=0)
    Comment = models.TextField('توضیحات', db_column='Comment', null=True, blank=True)

    def __str__(self):
        return str(self.YearWorkingPeriod)

    class Meta:
        verbose_name = 'فرایند استخراج داده'
        verbose_name_plural = 'فرایند استخراج داده'
        db_table = 'ETL_YearWorkingPeriod'

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)

        self.Comment = ETL_async.delay(self.YearWorkingPeriod)

        super(YearWorkingPeriod, self).save(*args, **kwargs)

