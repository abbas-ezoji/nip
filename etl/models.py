from django.db import models
from nip.tasks import ETL_async
from django.db.models import Q


States = (
    (0, ("بسته شده")),
    (1, ("جاری")),
    (2, ("بعدی")),
)

EtlStates = (
    (0, ("خاموش")),
    (1, ("روشن")),
)


class YearWorkingPeriod(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    YearWorkingPeriod = models.IntegerField('سال-دوره', db_column='YearWorkingPeriod')
    State = models.IntegerField('وضعیت', db_column='State', choices=States, default=0)
    EtlState = models.IntegerField('.ضعیت استخراج', db_column='EtlState', choices=EtlStates, default=0)
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

        # self.Comment = ETL_async.delay(self.YearWorkingPeriod)

        # if self.State>0:
        #     q = ~Q(id=3)
        #     all_period = self.obetjcts.filter(State=self.State)
        #     if self.instance.pk is not None:
        #         all_period = all_period.exclude(pk=self.instance.pk)
        #
        #     all_period.State = 0
        #     all_period.save()

        super(YearWorkingPeriod, self).save(*args, **kwargs)

