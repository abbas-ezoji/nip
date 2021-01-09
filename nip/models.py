import pandas as pd
from django.db import models
from django.utils.html import format_html
from django.contrib.auth.models import User
from nip.tasks import set_shift_async
from django.contrib import messages
from sqlalchemy import create_engine
from project.db import get_db

DATABASES = get_db()
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


class ShiftTypes(models.Model):
    Code = models.CharField('کد', max_length=5)
    Title = models.CharField('عنوان', max_length=50)

    def __str__(self):
        return self.Title

    class Meta:
        verbose_name_plural = 'نوع شیفت'


class PersonnelTypes(models.Model):
    Code = models.CharField('کد', max_length=5)
    Title = models.CharField('عنوان', max_length=50)
    ExternalId = models.IntegerField('شناسه دیدگاه', null=True, blank=True)
    ExternalGuid = models.CharField('شناسه شاخص دیدگاه', max_length=60, null=True, blank=True)

    def __str__(self):
        return self.Title

    class Meta:
        verbose_name_plural = 'پرسنل - تخصص'


class Personnel(models.Model):
    PersonnelNo = models.CharField('شماره پرسنلی', max_length=100, null=True, blank=True, )
    FullName = models.CharField('نام کامل', max_length=100)
    WorkSection = models.ForeignKey(WorkSection, verbose_name=u'بخش', on_delete=models.CASCADE)
    YearWorkingPeriod = models.IntegerField('سال-دوره', )
    RequirementWorkMins_esti = models.IntegerField('زمان پیش بینی شده', )
    PersonnelTypes = models.ForeignKey(PersonnelTypes, verbose_name=u'تخصص', on_delete=models.CASCADE)
    EfficiencyRolePoint = models.FloatField('امتیاز بهره وری', )
    ExternalId = models.IntegerField('شناسه دیدگاه', null=True, blank=True)
    ExternalGuid = models.CharField('شناسه شاخص دیدگاه', max_length=60, null=True, blank=True)

    def __str__(self):
        return self.FullName + ' - ' + self.PersonnelTypes.Title

    class Meta:
        verbose_name_plural = 'پرسنل'


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


class HardConstraints(models.Model):
    Personnel = models.ForeignKey(Personnel, verbose_name=u'پرسنل', on_delete=models.CASCADE)
    YearWorkingPeriod = models.IntegerField('سال-دوره', )
    Day = models.IntegerField('روز', )
    ShiftType = models.ForeignKey(ShiftTypes, verbose_name='نوع شیفت', on_delete=models.CASCADE,
                                  db_column='ShiftType_id', null=True, blank=True)
    Value = models.IntegerField('مقدار', null=True, blank=True)
    ExternalId = models.IntegerField('شناسه دیدگاه', null=True, blank=True)
    ExternalGuid = models.CharField('شناسه شاخص دیدگاه', max_length=60, null=True, blank=True)

    def __str__(self):
        return self.Personnel.FullName + ' - ' + str(self.Day) + ' - ' + str(self.Value)

    class Meta:
        verbose_name_plural = 'پرسنل - قیدهای تایید شده'
        db_table = 'nip_hardconstraints'


class PersonnelRequest(models.Model):
    Personnel = models.ForeignKey(Personnel, verbose_name=u'پرسنل', on_delete=models.CASCADE)
    YearWorkingPeriod = models.IntegerField('سال-دوره', )
    Day = models.IntegerField('روز', )
    ShiftType = models.ForeignKey(ShiftTypes, verbose_name=u'نوع شیفت', on_delete=models.CASCADE)
    Value = models.IntegerField('مقدار', )

    def __str__(self):
        return self.Personnel.Title + ' - ' + self.ShiftType.Title + ' - ' + str(self.Value)

    class Meta:
        verbose_name_plural = 'پرسنل - خوداظهاری'


class ShiftAssignments(models.Model):
    WorkSection = models.ForeignKey(WorkSection, verbose_name=u'بخش', on_delete=models.CASCADE)
    YearWorkingPeriod = models.IntegerField('سال-دوره')
    Rank = models.IntegerField('رتبه', )
    Cost = models.FloatField('هزینه', )
    EndTime = models.BigIntegerField('زمان تکمیل', null=True)
    UsedParentCount = models.IntegerField('تعداد مصرف', )
    present_id = models.CharField('شناسه', null=True, max_length=50, editable=False)

    def __str__(self):
        return self.WorkSection.Title + str(self.YearWorkingPeriod) + ' -> ' + str(self.Rank)

    class Meta:
        verbose_name_plural = 'شیفت پیشنهادی - جزئیات'


class PersonnelShiftDateAssignments(models.Model):
    ShiftAssignment = models.ForeignKey(ShiftAssignments, on_delete=models.CASCADE, null=True)
    Personnel = models.ForeignKey(Personnel, verbose_name=u'پرسنل', on_delete=models.CASCADE, null=True)
    YearWorkingPeriod = models.IntegerField('سال-دوره', null=True, editable=False)
    D01 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, db_column='D01', null=True)
    D02 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D02', db_column='D02', null=True)
    D03 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D03', db_column='D03', null=True)
    D04 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D04', db_column='D04', null=True)
    D05 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D05', db_column='D05', null=True)
    D06 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D06', db_column='D06', null=True)
    D07 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D07', db_column='D07', null=True)
    D08 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D08', db_column='D08', null=True)
    D09 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D09', db_column='D09', null=True)
    D10 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D10', db_column='D10', null=True)
    D11 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D11', db_column='D11', null=True)
    D12 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D12', db_column='D12', null=True)
    D13 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D13', db_column='D13', null=True)
    D14 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D14', db_column='D14', null=True)
    D15 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D15', db_column='D15', null=True)
    D16 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D16', db_column='D16', null=True)
    D17 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D17', db_column='D17', null=True)
    D18 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D18', db_column='D18', null=True)
    D19 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D19', db_column='D19', null=True)
    D20 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D20', db_column='D20', null=True)
    D21 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D21', db_column='D21', null=True)
    D22 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D22', db_column='D22', null=True)
    D23 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D23', db_column='D23', null=True)
    D24 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D24', db_column='D24', null=True)
    D25 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D25', db_column='D25', null=True)
    D26 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D26', db_column='D26', null=True)
    D27 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D27', db_column='D27', null=True)
    D28 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D28', db_column='D28', null=True)
    D29 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D29', db_column='D29', null=True)
    D30 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D30', db_column='D30', null=True)
    D31 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D31', db_column='D31', null=True)

    def __str__(self):
        return self.Personnel.FullName

    class Meta:
        verbose_name_plural = 'شیفت پیشنهادی - آرشیو '


class ShiftConstDayRequirements(models.Model):
    ShiftAssignment = models.ForeignKey(ShiftAssignments, on_delete=models.CASCADE, null=True)
    Day = models.IntegerField('روز')
    PersonnelTypes = models.ForeignKey(PersonnelTypes, verbose_name=u'تخصص', on_delete=models.DO_NOTHING)
    ShiftTypes = models.IntegerField('نوع شیفت', db_column='ShiftTypes_id')
    PersonnelCount = models.IntegerField('تعدا پرسنل اختصاص داده شده')
    PersonnelPoints = models.IntegerField('مجموع امتیاز پرسنل')
    RequireMinCount = models.IntegerField('حداقل تعداد نیاز')
    RequireMaxCount = models.IntegerField('حداکثر تعاد نیاز')
    RequireMeanCount = models.IntegerField(editable=False)
    DiffMinCount = models.IntegerField(editable=False)
    DiffMaxCount = models.IntegerField(editable=False)
    DiffCount = models.IntegerField('اختلاف')

    def __str__(self):
        return str(self.Day) + '-' + str(self.PersonnelTypes.Title) + '-' + str(self.ShiftTypes)

    class Meta:
        verbose_name_plural = 'نیازمندی روزانه'


class ShiftConstPersonnelTimes(models.Model):
    ShiftAssignment = models.ForeignKey(ShiftAssignments, on_delete=models.CASCADE, null=True)
    Personnel = models.ForeignKey(Personnel, verbose_name=u'پرسنل', on_delete=models.CASCADE)
    PersonnelTypes = models.ForeignKey(PersonnelTypes, verbose_name=u'تخصص', on_delete=models.DO_NOTHING)
    EfficiencyRolePoint = models.IntegerField('امتیاز بهره وری')
    RequireMinsEstimate = models.IntegerField('زمان نیاز بهره وری')
    ExtraForce = models.IntegerField('مجمع زمان اجباری', null=True)
    AssignedTimes = models.IntegerField('مقدار زمان اختصاص داده شده')
    Diff = models.IntegerField('اختلاف')

    def __str__(self):
        return str(self.Personnel.FullName) + '-' + str(self.PersonnelTypes.Title) + '-' + str(self.EfficiencyRolePoint)

    class Meta:
        verbose_name_plural = 'اختلاف زمانی پرسنل'


class WorkSectionRequirements(models.Model):
    WorkSection = models.ForeignKey(WorkSection, verbose_name=u'بخش', on_delete=models.CASCADE)
    Year = models.IntegerField('سال', )
    Month = models.IntegerField('دوره', )
    DayType = models.IntegerField('نوع روز', )
    PersonnelTypeReq = models.ForeignKey(PersonnelTypes, verbose_name=u'تخصص', on_delete=models.CASCADE)
    ShiftType = models.ForeignKey(ShiftTypes, verbose_name=u'نوع شیفت', on_delete=models.CASCADE)
    ReqMinCount = models.IntegerField('حداقل', )
    ReqMaxCount = models.IntegerField('حداکثر', )
    day_diff_typ = models.IntegerField('تفاوت', null=True, blank=True)
    Date = models.IntegerField('تاریخ', null=True, blank=True)
    PersonnelTypeReqCount = models.IntegerField('تعداد پرسنل', null=True, blank=True)

    def __str__(self):
        return self.WorkSection.Title + ' - ' + self.PersonnelTypeReq.Title + ' - ' + self.ShiftType.Title

    class Meta:
        verbose_name_plural = 'بخش - نیازمندی ها'


class tkp_Logs(models.Model):
    Personnel = models.ForeignKey(Personnel, verbose_name='پرسنل', on_delete=models.DO_NOTHING)
    Date = models.DateField()
    Login = models.IntegerField()
    Logout = models.IntegerField()
    DayDisposition = models.IntegerField()
    YearWorkingPeriodId = models.IntegerField()
    LoginDayDisposition = models.IntegerField()
    ExternalId = models.IntegerField('شناسه دیدگاه', null=True, blank=True)
    ExternalGuid = models.CharField('شناسه شاخص دیدگاه', max_length=60, null=True, blank=True)

    def __str__(self):
        return self.Personnel + ' - ' + str(self.Date) + ' - ' + str(self.Login) + ' - ' + str(self.Logout)

    class Meta:
        verbose_name_plural = 'Time Logs'


recommender_status = (
    (0, ("بهینه سازی")),
    (1, ("ایجاد جدید")),
)

task_status = (
    (0, ("خاموش")),
    (1, ("روشن")),
    (2, ("بازیابی اطلاعات و اجرای مجدد")),
)


class ShiftRecommendManager(models.Model):
    WorkSection = models.ForeignKey(WorkSection, verbose_name=u'بخش', on_delete=models.CASCADE)
    YearWorkingPeriod = models.IntegerField('سال-دوره')
    coh_const_DayRequirements = models.FloatField('ضریب قید نیاز روزانه')
    coh_const_PersonnelPerformanceTime = models.FloatField('ضریب قید نفرساعت بهره وری')
    TaskStatus = models.IntegerField('وضعیت کل سیستم', choices=task_status, default=0)
    RecommenderStatus = models.IntegerField('وضعیت پیشنهاددهنده', choices=recommender_status, default=0)
    PopulationSize = models.IntegerField('تعداد جمعیت', default=80)
    GenerationCount = models.IntegerField('تعداد نسل', default=200)
    MaxFitConstRate = models.FloatField('حداکثر نرخ ثبات هزینه', default=0.3)
    CrossoverProbability = models.FloatField('نرخ جستجوی محلی', default=0.3)
    MutationProbability = models.FloatField('نرخ جستجوی غیرمحلی', default=0.3)
    Elitism = models.BooleanField('نابغه گرایی', default=False)
    ShowPlot = models.BooleanField('نمایش نمودار هزینه', default=False)
    DevByParent = models.BooleanField('توسعه والد', default=True)
    Comments = models.TextField('شرح', null=True, blank=True)

    TaskLevelDone = models.IntegerField(default=0,
                                        editable=False)  # 0=(no fetch data from ERP) and 1=(fetched date and run recommender)

    def __str__(self):
        return self.WorkSection.Title + '-' + str(self.YearWorkingPeriod)

    class Meta:
        verbose_name_plural = 'مدیریت - سیستم هوشمند شیفت'

    def save(self, *args, **kwargs):
        if not self.id or self.TaskStatus == 0:
            super().save(*args, **kwargs)

        pers_count = pd.read_sql_query('''SELECT COUNT(*) FROM [nip_personnel]
                    WHERE [YearWorkingPeriod]={} AND [WorkSection_id] = {}
                    '''.format(self.YearWorkingPeriod, self.WorkSection.id), engine)
        print(pers_count)
        if len(pers_count) == 0:
            messages.error('Don\'t Save', messages.ERROR)
            return

        if self.TaskStatus == 1:  # just run optimizer
            self.Comments = set_shift_async.delay(self.WorkSection.id,
                                                  self.YearWorkingPeriod,
                                                  self.coh_const_DayRequirements,
                                                  self.coh_const_PersonnelPerformanceTime,
                                                  self.PopulationSize,
                                                  self.GenerationCount,
                                                  self.MaxFitConstRate,
                                                  self.CrossoverProbability,
                                                  self.MutationProbability,
                                                  self.Elitism,
                                                  self.ShowPlot,
                                                  self.DevByParent,
                                                  self.RecommenderStatus
                                                  )
        elif self.TaskStatus == 2:

            self.Comments = set_shift_async.delay(self.WorkSection.id,
                                                  self.YearWorkingPeriod,
                                                  self.coh_const_DayRequirements,
                                                  self.coh_const_PersonnelPerformanceTime,
                                                  self.PopulationSize,
                                                  self.GenerationCount,
                                                  self.MaxFitConstRate,
                                                  self.CrossoverProbability,
                                                  self.MutationProbability,
                                                  self.Elitism,
                                                  self.ShowPlot,
                                                  self.DevByParent,
                                                  self.RecommenderStatus
                                                  )
        super(ShiftRecommendManager, self).save(*args, **kwargs)
