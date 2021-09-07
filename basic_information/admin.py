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
from authentication import models as authentication
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

    def get_queryset(self, request):
        qs = super(HospitalAdmin, self).get_queryset(request)
        user = request.user
        user_profile = authentication.UserProfile.objects.filter(User=user)[0]
        if user.is_superuser or user_profile.Level == 1:
            return qs
        hospital = user_profile.Hospital.id
        work_section = user_profile.WorkSection.id

        if user_profile.Level == 2:
            return qs.filter(id=hospital)
        if user_profile.Level == 3:
            return qs.filter(id=hospital)

    def view_personnel_link(self, obj):
        count = obj.worksection_set.count()
        url = (
                reverse("admin:basic_information_worksection_changelist")
                + "?"
                + urlencode({"hospital__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} تعداد بخش</a>', url, count)

    view_personnel_link.short_description = "مجموع بخشها"


class WorkSectionFilter(admin.SimpleListFilter):
    title = 'بخش'
    parameter_name = 'WorkSection'

    def lookups(self, request, model_admin):
        if 'WorkSection__Hospital__id__exact' in request.GET:
            id = request.GET['WorkSection__Hospital__id__exact']
            WorkSection = set([c.WorkSection for c in model_admin.model.objects.all().filter(WorkSection__Hospital__id=id)])
        else:
            WorkSection = set([c.WorkSection for c in model_admin.model.objects.all()])
        return [(c.id, c.Title) for c in WorkSection]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(WorkSection__id__exact=self.value())


@admin.register(WorkSection)
class WorkSectionAdmin(admin.ModelAdmin):
    list_display = ('Title', 'Hospital', 'ExternalId', 'view_personnel_link',)
    list_filter = ('Code', 'Title', 'Hospital',)

    def render_change_form(self, request, context, *args, **kwargs):
        user = request.user
        user_profile = authentication.UserProfile.objects.filter(User=user)[0]
        if user.is_superuser or user_profile.Level == 1:
            return super(WorkSectionAdmin, self).render_change_form(request, context, *args, **kwargs)

        hospital = user_profile.Hospital.id
        work_section = user_profile.WorkSection.id
        context['adminform'].form.fields['Hospital'].queryset = Hospital.objects.filter(id=hospital)
        return super(WorkSectionAdmin, self).render_change_form(request, context, *args, **kwargs)

    def get_queryset(self, request):
        qs = super(WorkSectionAdmin, self).get_queryset(request)
        user = request.user
        user_profile = authentication.UserProfile.objects.filter(User=user)[0]
        if user.is_superuser or user_profile.Level == 1:
            return qs
        hospital = user_profile.Hospital.id
        work_section = user_profile.WorkSection.id

        if user_profile.Level == 2:
            return qs.filter(Hospital__id=hospital)
        if user_profile.Level == 3:
            return qs.filter(id=work_section)

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
                    'PersonnelTypes', 'RequirementWorkMins_esti', 'EfficiencyRolePoint', 'User')
    list_filter = ('YearWorkingPeriod',
                   ('WorkSection__Hospital', admin.RelatedOnlyFieldListFilter), WorkSectionFilter,
                   'PersonnelNo', 'FullName',
                   'PersonnelTypes', 'Active', 'User')

    def render_change_form(self, request, context, *args, **kwargs):
        user = request.user
        user_profile = authentication.UserProfile.objects.filter(User=user)[0]
        if user.is_superuser or user_profile.Level == 1:
            return super(PersonnelAdmin, self).render_change_form(request, context, *args, **kwargs)

        hospital = user_profile.Hospital.id
        work_section = user_profile.WorkSection.id
        if user_profile.Level == 2:
            context['adminform'].form.fields['WorkSection'].queryset = WorkSection.objects.filter(Hospital__id=hospital)
        if user_profile.Level == 3:
            context['adminform'].form.fields['WorkSection'].queryset = WorkSection.objects.filter(id=work_section)
        return super(PersonnelAdmin, self).render_change_form(request, context, *args, **kwargs)

    def get_queryset(self, request):
        qs = super(PersonnelAdmin, self).get_queryset(request)
        user = request.user
        user_profile = authentication.UserProfile.objects.filter(User=user)[0]
        if user.is_superuser or user_profile.Level == 1:
            return qs
        hospital = user_profile.Hospital.id
        work_section = user_profile.WorkSection.id

        if user_profile.Level == 2:
            return qs.filter(WorkSection__Hospital__id=hospital)
        if user_profile.Level == 3:
            return qs.filter(WorkSection__id=work_section)
