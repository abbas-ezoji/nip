import pandas as pd
from django.db import models
from django.utils.html import format_html
from django.contrib.auth.models import User
from nip.tasks import set_shift_async
from django.contrib import messages
from sqlalchemy import create_engine
from project.db import get_dbs
from etl import models as etl


DATABASES = get_dbs()
USER = DATABASES['nip']['USER']
PASSWORD = DATABASES['nip']['PASSWORD']
HOST = DATABASES['nip']['HOST']
# PORT = DATABASES['nip']['PORT']
NAME = DATABASES['nip']['NAME']

engine = create_engine('mssql+pyodbc://{}:{}@{}/{}?driver=SQL+Server' \
                       .format(USER,
                               PASSWORD,
                               HOST,
                               NAME
                               ))


class Dim_Date(models.Model):
    Date = models.DateField(null=True, blank=True)
    PersianDate = models.CharField(max_length=10)
    SpecialDay = models.IntegerField()
    PersianYear = models.IntegerField()
    PersianYearTitle = models.CharField(max_length=20)
    FiscalYear = models.IntegerField()
    WorkingPeriodYear = models.IntegerField(null=True, blank=True)
    WorkingPeriod = models.IntegerField(null=True, blank=True)
    WorkingPeriodTitle = models.CharField(max_length=20, null=True, blank=True)
    PersianSemester = models.FloatField()
    PersianSemesterTitle = models.CharField(max_length=20)
    PersianQuarter = models.FloatField()
    PersianQuarterTitle = models.CharField(max_length=20)
    PersianMonth = models.FloatField()
    PersianMonthTitle = models.CharField(max_length=20)
    PersianWeekNumberOfYear = models.FloatField()
    PersianWeekNumberOfMonth = models.FloatField()
    PersianDayOfMonth = models.FloatField()
    PersianDayOfYear = models.FloatField()
    PersianWeekDay = models.FloatField()
    PersianWeekDayTitle = models.CharField(max_length=20)

    def __str__(self):
        return str(self.PersianYear) + str(self.PersianMonth) + str(self.PersianDayOfMonth)

    class Meta:
        verbose_name_plural = 'تاریخ'
        db_table = 'nip_dim_date'


class Hospital(models.Model):
    Code = models.CharField('کد', max_length=5)
    Title = models.CharField('عنوان', max_length=50)
    ExternalId = models.IntegerField('شناسه دیدگاه', null=True, blank=True)
    ExternalGuid = models.CharField('شناسه شاخص دیدگاه', max_length=60, null=True, blank=True)

    def __str__(self):
        return self.Title

    class Meta:
        verbose_name = 'بیمارستان'
        verbose_name_plural = 'بیمارستان'
        db_table = 'nip_hospital'


class WorkSection(models.Model):
    Hospital = models.ForeignKey(Hospital, verbose_name=u'بیمارستان', on_delete=models.CASCADE)
    Code = models.CharField('کد', max_length=5)
    Title = models.CharField('عنوان', max_length=50)
    ExternalId = models.IntegerField('شناسه دیدگاه', null=True, blank=True)
    ExternalGuid = models.CharField('شناسه شاخص دیدگاه', max_length=60, null=True, blank=True)

    def __str__(self):
        return self.Hospital.Title + '->' + self.Title

    class Meta:
        verbose_name = 'بخش'
        verbose_name_plural = 'بخش'
        db_table = 'nip_worksection'


class ShiftTypes(models.Model):
    Code = models.CharField('کد', max_length=5)
    Title = models.CharField('عنوان', max_length=50)

    def __str__(self):
        return self.Code

    class Meta:
        verbose_name_plural = 'نوع شیفت'
        db_table = 'nip_shifttypes'


class PersonnelTypes(models.Model):
    Code = models.CharField('کد', max_length=5)
    Title = models.CharField('عنوان', max_length=50)
    ExternalId = models.IntegerField('شناسه دیدگاه', null=True, blank=True)
    ExternalGuid = models.CharField('شناسه شاخص دیدگاه', max_length=60, null=True, blank=True)

    def __str__(self):
        return self.Title

    class Meta:
        verbose_name_plural = 'پرسنل - تخصص'
        db_table = 'nip_personneltypes'


class Personnel(models.Model):
    PersonnelNo = models.CharField('شماره پرسنلی', max_length=100, null=True, blank=True, )
    FullName = models.CharField('نام کامل', max_length=100)
    WorkSection = models.ForeignKey(WorkSection, verbose_name=u'بخش', on_delete=models.CASCADE)
    YearWorkingPeriod = models.ForeignKey(etl.YearWorkingPeriod, verbose_name=u'سال-دوره',
                                          on_delete=models.CASCADE, db_column='YearWorkingPeriod')
    RequirementWorkMins_esti = models.IntegerField('زمان پیش بینی شده', )
    PersonnelTypes = models.ForeignKey(PersonnelTypes, verbose_name=u'تخصص', on_delete=models.DO_NOTHING)
    EfficiencyRolePoint = models.FloatField('امتیاز بهره وری', )
    ExternalId = models.IntegerField('شناسه دیدگاه', null=True, blank=True)
    ExternalGuid = models.CharField('شناسه شاخص دیدگاه', max_length=60, null=True, blank=True)
    Active = models.IntegerField('فعال', default=1)
    User = models.ForeignKey(User, verbose_name=u'کاربر',
                                on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return self.FullName

    class Meta:
        verbose_name_plural = 'پرسنل'
        db_table = 'nip_personnel'


class Shifts(models.Model):
    Code = models.IntegerField('کد', )
    Title = models.CharField('عنوان', max_length=100)
    Length = models.IntegerField('میزان', )
    StartTime = models.IntegerField('شروع', )
    EndTime = models.IntegerField('پایان', )
    Type = models.CharField('نوع شیفت', max_length=3, null=True, blank=True)
    ExternalId = models.IntegerField('شناسه دیدگاه', null=True, blank=True)
    ExternalGuid = models.CharField('شناسه شاخص دیدگاه', max_length=60, null=True, blank=True)

    def __str__(self):
        return self.Title

    class Meta:
        verbose_name_plural = 'شیفت'
        db_table = 'nip_shifts'
