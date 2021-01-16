from django.contrib import admin
from .models import *


@admin.register(ETL)
class ETLAdmin(admin.ModelAdmin):
    list_display = ('YearWorkingPeriod', 'HospitalDepartmentCode', )
    list_filter = ('YearWorkingPeriod', 'HospitalDepartmentCode', )
