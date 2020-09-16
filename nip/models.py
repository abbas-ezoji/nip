from django.db import models
from django.utils.html import format_html
from django.contrib.auth.models import User


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


class WorkSection(models.Model):
    Code = models.CharField('کد', max_length=5)
    Title = models.CharField('عنوان', max_length=50)
    ExternalId = models.IntegerField('شناسه دیدگاه', null=True, blank=True)
    ExternalGuid = models.CharField('شناسه شاخص دیدگاه', max_length=60, null=True, blank=True)

    def __str__(self):
        return self.Title

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
    PersonnelBaseId = models.IntegerField('شناسه پرسنلی')
    FullName = models.CharField('نام کامل', max_length=100)
    WorkSection = models.ForeignKey(WorkSection, on_delete=models.CASCADE)
    YearWorkingPeriod = models.IntegerField('سال-دوره', editable=False)
    RequirementWorkMins_esti = models.IntegerField('زمان پیش بینی شده', )
    RequirementWorkMins_real = models.IntegerField('زمان اختصاص داده شده', )
    PersonnelTypes = models.ForeignKey(PersonnelTypes, on_delete=models.CASCADE)
    EfficiencyRolePoint = models.IntegerField('امتیاز بهره وری', )
    DiffNorm = models.IntegerField(null=True, blank=True, editable=False)
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


class PersonnelLeaves(models.Model):
    Personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    YearWorkingPeriod = models.IntegerField('سال-دوره', )
    Day = models.IntegerField('روز', )
    Value = models.IntegerField('مقدار', null=True, blank=True)
    ExternalId = models.IntegerField('شناسه دیدگاه', null=True, blank=True)
    ExternalGuid = models.CharField('شناسه شاخص دیدگاه', max_length=60, null=True, blank=True)

    def __str__(self):
        return self.Personnel.FullName + ' - ' + str(self.Day) + ' - ' + str(self.Value)

    class Meta:
        verbose_name_plural = 'پرسنل - مرخصی تایید شده'


class PersonnelRequest(models.Model):
    Personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    YearWorkingPeriod = models.IntegerField('سال-دوره', )
    Day = models.IntegerField('روز', )
    ShiftType = models.ForeignKey(ShiftTypes, on_delete=models.CASCADE)
    Value = models.IntegerField('مقدار', )

    def __str__(self):
        return self.Personnel.Title + ' - ' + self.ShiftType.Title + ' - ' + str(self.Value)

    class Meta:
        verbose_name_plural = 'پرسنل - خوداظهاری'


class ShiftAssignments(models.Model):
    WorkSection = models.ForeignKey(WorkSection, on_delete=models.CASCADE)
    YearWorkingPeriod = models.IntegerField('سال-دوره', editable=False)
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
    Personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, null=True)
    YearWorkingPeriod = models.IntegerField('سال-دوره', null=True, editable=False)
    D01 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, default=1, db_column='D01')
    D02 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D02', db_column='D02')
    D03 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D03', db_column='D03')
    D04 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D04', db_column='D04')
    D05 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D05', db_column='D05')
    D06 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D06', db_column='D06')
    D07 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D07', db_column='D07')
    D08 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D08', db_column='D08')
    D09 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D09', db_column='D09')
    D10 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D10', db_column='D10')
    D11 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D11', db_column='D11')
    D12 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D12', db_column='D12')
    D13 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D13', db_column='D13')
    D14 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D14', db_column='D14')
    D15 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D15', db_column='D15')
    D16 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D16', db_column='D16')
    D17 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D17', db_column='D17')
    D18 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D18', db_column='D18')
    D19 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D19', db_column='D19')
    D20 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D20', db_column='D20')
    D21 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D21', db_column='D21')
    D22 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D22', db_column='D22')
    D23 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D23', db_column='D23')
    D24 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D24', db_column='D24')
    D25 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D25', db_column='D25')
    D26 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D26', db_column='D26')
    D27 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D27', db_column='D27')
    D28 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D28', db_column='D28')
    D29 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D29', db_column='D29')
    D30 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D30', db_column='D30')
    D31 = models.ForeignKey(Shifts, on_delete=models.DO_NOTHING, related_name='D31', db_column='D31')

    def __str__(self):
        return self.Personnel.FullName

    class Meta:
        verbose_name_plural = 'شیفت پیشنهادی - آرشیو '


class ShiftConstDayRequirements(models.Model):
    ShiftAssignment = models.ForeignKey(ShiftAssignments, on_delete=models.CASCADE, null=True)
    Day = models.IntegerField('روز')
    PersonnelTypes = models.ForeignKey(PersonnelTypes, on_delete=models.DO_NOTHING)
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
    Personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    PersonnelTypes = models.ForeignKey(PersonnelTypes, on_delete=models.DO_NOTHING)
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
    WorkSection = models.ForeignKey(WorkSection, on_delete=models.CASCADE)
    Year = models.IntegerField('سال', )
    Month = models.IntegerField('دوره', )
    DayType = models.IntegerField('نوع روز', )
    PersonnelTypeReq = models.ForeignKey(PersonnelTypes, on_delete=models.CASCADE)
    ShiftType = models.ForeignKey(ShiftTypes, on_delete=models.CASCADE)
    ReqMinCount = models.IntegerField('حداقل', )
    ReqMaxCount = models.IntegerField('حداکثر', )
    day_diff_typ = models.IntegerField('تفاوت', null=True, blank=True)
    Date = models.IntegerField('تاریخ', null=True, blank=True)
    PersonnelTypeReqCount = models.IntegerField('تعداد پرسنل', null=True, blank=True)

    def __str__(self):
        return self.WorkSection.Title + ' - ' + self.PersonnelTypeReq.Title + ' - ' + self.ShiftType.Title

    class Meta:
        verbose_name_plural = 'بخش - نیزمندی ها'


class tkp_Logs(models.Model):
    Personnel = models.ForeignKey(Personnel, on_delete=models.DO_NOTHING)
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


recommander_status = (
    (0, ("بهینه سازی")),
    (1, ("ایجاد جدید")),
)

task_status = (
    (0, ("خاموش")),
    (1, ("روشن")),
    (2, ("بازیابی اطلاعات و اجرای مجدد")),
)


class ShiftRecommandManager(models.Model):
    WorkSection = models.ForeignKey(WorkSection, on_delete=models.CASCADE)
    YearWorkingPeriod = models.IntegerField('سال-دوره')
    coh_const_DayRequirements = models.FloatField('ضریب قید نیاز روزانه')
    coh_const_coh_PersonnelPerformanceTime = models.FloatField('ضریب قید نفرساعت بهره وری')
    TaskStatus = models.IntegerField('وضعیت کل سیستم', choices=task_status, default=0)
    RecommanderStatus = models.IntegerField('وضعیت پیشنهاددهنده', choices=recommander_status, default=0)
    PopulationSize = models.IntegerField('تعداد جمعیت', default=80)
    GenerationCount = models.IntegerField('تعداد نسل', default=200)
    MaxFitConstRate = models.FloatField('حداکثر نرخ ثبات هزینه', default=0.3)
    CrossoverProbability = models.FloatField('نرخ جستجوی محلی', default=0.3)
    MutationProbability = models.FloatField('نرخ جستجوی غیرمحلی', default=0.3)
    Elitism = models.BooleanField('نابغه گرایی', default=False)
    ShowPlot = models.BooleanField('نمایش نمودار هزینه', default=False)
    DevByParent = models.BooleanField('توسعه والد', default=True)

    TaskLevelDone = models.IntegerField(default=0, editable=False)  # 0=(no fetch data from ERP) and 1=(fetched date and run recommander)

    def __str__(self):
        return self.WorkSection.Title + '-' + str(self.YearWorkingPeriod)

    class Meta:
        verbose_name_plural = 'مدیریت - سیستم هوشمند شیفت'
