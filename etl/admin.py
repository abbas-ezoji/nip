from django.contrib import admin
from .models import *


@admin.register(YearWorkingPeriod)
class YearWorkingPeriodAdmin(admin.ModelAdmin):
    list_display = ('YearWorkingPeriod', 'State',)
    list_filter = ('YearWorkingPeriod', 'State', )


