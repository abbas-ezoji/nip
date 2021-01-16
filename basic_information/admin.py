import json
import csv

from django.contrib import admin
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.http import JsonResponse
from django.urls import path

from django.utils.html import format_html
from django import forms
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib import admin
from .models import *
from nip.tasks import update_shift_async, test
import io
from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.http import FileResponse
from reportlab.pdfgen import canvas
from tabbed_admin import TabbedModelAdmin


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('Code', 'Title', 'ExternalId', 'view_personnel_link',)
    list_filter = ('Code', 'Title')

    # search_fields = ("Title",)

    def view_personnel_link(self, obj):
        count = obj.worksection_set.count()
        url = (
                reverse("admin:basic_information_worksection_changelist")
                + "?"
                + urlencode({"hospital__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} تعداد بخش</a>', url, count)

    view_personnel_link.short_description = "مجموع بخشها"


@admin.register(WorkSection)
class WorkSectionAdmin(admin.ModelAdmin):
    list_display = ('Title', 'Hospital', 'ExternalId', 'view_personnel_link',)
    list_filter = ('Code', 'Title', 'Hospital',)

    # search_fields = ("Title",)

    def view_personnel_link(self, obj):
        count = obj.personnel_set.count()
        url = (
                reverse("admin:basic_information_personnel_changelist")
                + "?"
                + urlencode({"WorkSection__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} تعداد پرسنل</a>', url, count)

    view_personnel_link.short_description = "مجموع پرسنل"


@admin.register(PersonnelTypes)
class PersonnelTypesAdmin(admin.ModelAdmin):
    list_display = ('Code', 'Title')
    list_filter = ('Code', 'Title')


@admin.register(Shifts)
class ShiftsAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Shifts._meta.get_fields()]
    list_display = ('Code', 'Title', 'Length', 'ExternalId', 'type_colored',)
    list_filter = ('Code', 'Title', 'Length',)

    def type_colored(self, obj):
        color_dict = {'0': 'white',
                      '1': 'green',
                      '2': 'red',
                      '3': 'blue',
                      '12': 'orange',
                      '13': 'brown',
                      '23': 'Purple',
                      }

        return format_html(
            ''' <input style="background:{};"/> 
                '''.format(color_dict.get(obj.Type)))


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('YearWorkingPeriod', 'WorkSection', 'PersonnelNo', 'FullName',
                    'PersonnelTypes', 'RequirementWorkMins_esti', 'EfficiencyRolePoint')
    list_filter = ('YearWorkingPeriod', 'WorkSection__Hospital', 'WorkSection', 'PersonnelNo', 'FullName',
                   'PersonnelTypes', 'Active')
