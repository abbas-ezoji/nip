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


class PersonnelShiftDateAssignmentsInline(admin.TabularInline):
    model = PersonnelShiftDateAssignments
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        """
        Override the formset function in order to remove the add and change buttons beside the foreign key pull-down
        menus in the inline.
        """
        formset = super(PersonnelShiftDateAssignmentsInline, self).get_formset(request, obj, **kwargs)
        form = formset.form
        widget = form.base_fields['Personnel'].widget
        widget.can_add_related = False
        widget.can_change_related = False
        widget.can_delete_related = False
        for d in range(1, 32):
            day = 'D' + (str(d) if d > 9 else '0' + str(d))
            widget = form.base_fields[day].widget
            widget.can_add_related = False
            widget.can_change_related = False
            widget.can_delete_related = False
        return formset


class ShiftConstDayRequirementsInline(admin.TabularInline):
    model = ShiftConstDayRequirements
    extra = 0
    ordering = ("-DiffCount", "Day", "PersonnelTypes", "ShiftTypes",)

    # readonly_fields = ([f for f in ShiftConstDayRequirements._meta.get_fields()])
    can_delete = False

    def get_queryset(self, request):
        qs = super(ShiftConstDayRequirementsInline, self).get_queryset(request)
        return qs.filter(DiffCount__gt=0)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(ShiftConstDayRequirementsInline, self).get_formset(request, obj, **kwargs)
        form = formset.form
        widget = form.base_fields['PersonnelTypes'].widget
        widget.can_add_related = False
        widget.can_change_related = False
        widget.can_delete_related = False

        return formset


class ShiftConstPersonnelTimesInline(admin.TabularInline):
    model = ShiftConstPersonnelTimes
    extra = 0
    ordering = ("-EfficiencyRolePoint", "PersonnelTypes",)
    can_delete = False

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(ShiftConstPersonnelTimesInline, self).get_formset(request, obj, **kwargs)
        form = formset.form
        widget = form.base_fields['PersonnelTypes'].widget
        widget.can_add_related = False
        widget.can_change_related = False
        widget.can_delete_related = False

        widget = form.base_fields['Personnel'].widget
        widget.can_add_related = False
        widget.can_change_related = False
        widget.can_delete_related = False

        return formset


@admin.register(ShiftAssignments)
class ShiftAssignmentsAdmin(TabbedModelAdmin):
    list_display = ('WorkSection', 'YearWorkingPeriod', 'Rank', 'Cost', 'EndTime', 'view_shifts_link')
    list_filter = ('WorkSection__Hospital', 'WorkSection', 'YearWorkingPeriod', 'Rank')
    readonly_fields = ('WorkSection', 'YearWorkingPeriod', 'Rank', 'Cost', 'EndTime')

    tab_overview = (
        (None, {
            'fields': ('WorkSection', 'YearWorkingPeriod', 'Rank', 'Cost', 'EndTime')
        }),
    )

    tab_PersonnelShiftDateAssignments = (
        PersonnelShiftDateAssignmentsInline,
    )
    tab_ShiftConstDayRequirementsInline = (
        ShiftConstDayRequirementsInline,
    )
    tab_ShiftConstPersonnelTimesInline = (
        ShiftConstPersonnelTimesInline,
    )

    tabs = [
        ('اصلی', tab_overview),
        ('شیفت اختصاصی', tab_PersonnelShiftDateAssignments),
        ('قید نیاز روز', tab_ShiftConstDayRequirementsInline),
        ('قید بهره وری', tab_ShiftConstPersonnelTimesInline),
    ]

    # inlines = [
    #     PersonnelShiftDateAssignmentsInline,
    #     ShiftConstDayRequirementsInline,
    #     ShiftConstPersonnelTimesInline,
    # ]

    def get_ordering(self, request):
        return ['WorkSection', 'YearWorkingPeriod', 'Rank']

    def view_shifts_link(self, obj):
        count = obj.personnelshiftdateassignments_set.count()
        url = (
                reverse("admin:nip_personnelshiftdateassignments_changelist")
                + "?"
                + urlencode({"ShiftAssignment__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">مشاهده شیفت </a>', url)

    view_shifts_link.short_description = "شیفتها"


class ShiftRecommendManagerForm(forms.ModelForm):
    class Meta:
        model = ShiftRecommendManager
        fields = "__all__"

    def clean_GenerationCount(self):
        if self.cleaned_data["GenerationCount"] > 200:
            raise forms.ValidationError("خطا در تعداد ...")

        return self.cleaned_data["GenerationCount"]


@admin.register(ShiftRecommendManager)
class ShiftRecommendManagerAdmin(admin.ModelAdmin):
    list_display = ('YearWorkingPeriod', 'WorkSection', 'coh_const_DayRequirements', 'coh_const_PersonnelPerformanceTime',
                    'TaskStatus', 'RecommenderStatus',)
    list_filter = ('YearWorkingPeriod', 'WorkSection', 'TaskStatus', 'RecommenderStatus',)
    # form = ShiftRecommendManagerForm


def zero_pad(num):
    return str(num) if num // 10 else '0' + str(num)


@admin.register(PersonnelShiftDateAssignments)
class PersonnelShiftDateAssignmentsAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in PersonnelShiftDateAssignments._meta.get_fields()]
    list_display = ('shift_colored',)
    list_filter = ('ShiftAssignment__WorkSection', 'YearWorkingPeriod',
                   'ShiftAssignment__Rank', )

    def shift_colored(self, obj):
        color_dict = {'0': 'white',
                      '1': 'green',
                      '2': 'red',
                      '3': 'blue',
                      '12': 'orange',
                      '13': 'brown',
                      '23': 'Purple',
                      }

        return format_html(
            ''' <b>{}</b> <p>{}</p>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>
                <td style="background:{};">{}</td>                                
            '''.format(obj.Personnel.FullName, obj.Personnel.PersonnelTypes.Title,
                       color_dict.get(obj.D01.Type), obj.D01.Type,
                       color_dict.get(obj.D02.Type), obj.D02.Type,
                       color_dict.get(obj.D03.Type), obj.D03.Type,
                       color_dict.get(obj.D04.Type), obj.D04.Type,
                       color_dict.get(obj.D05.Type), obj.D05.Type,
                       color_dict.get(obj.D06.Type), obj.D06.Type,
                       color_dict.get(obj.D07.Type), obj.D07.Type,
                       color_dict.get(obj.D08.Type), obj.D08.Type,
                       color_dict.get(obj.D09.Type), obj.D09.Type,
                       color_dict.get(obj.D10.Type), obj.D10.Type,
                       color_dict.get(obj.D11.Type), obj.D11.Type,
                       color_dict.get(obj.D12.Type), obj.D12.Type,
                       color_dict.get(obj.D13.Type), obj.D13.Type,
                       color_dict.get(obj.D14.Type), obj.D14.Type,
                       color_dict.get(obj.D15.Type), obj.D15.Type,
                       color_dict.get(obj.D16.Type), obj.D16.Type,
                       color_dict.get(obj.D17.Type), obj.D17.Type,
                       color_dict.get(obj.D18.Type), obj.D18.Type,
                       color_dict.get(obj.D19.Type), obj.D19.Type,
                       color_dict.get(obj.D20.Type), obj.D20.Type,
                       color_dict.get(obj.D20.Type), obj.D20.Type,
                       color_dict.get(obj.D22.Type), obj.D22.Type,
                       color_dict.get(obj.D23.Type), obj.D23.Type,
                       color_dict.get(obj.D24.Type), obj.D24.Type,
                       color_dict.get(obj.D25.Type), obj.D25.Type,
                       color_dict.get(obj.D26.Type), obj.D26.Type,
                       color_dict.get(obj.D27.Type), obj.D27.Type,
                       color_dict.get(obj.D28.Type), obj.D28.Type,
                       color_dict.get(obj.D29.Type), obj.D29.Type,
                       color_dict.get(obj.D30.Type), obj.D30.Type,
                       )
        )

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/pdf')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    def export_as_pdf(self, request, queryset):
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        # Start writing the PDF here
        for i, obj in enumerate(queryset):
            row = ''
            for j, field in enumerate(field_names):
                row += str(getattr(obj, field))
            p.drawString(1, 800 - (i * 10), row)
        # End writing

        # Close the PDF object cleanly, and we're done.
        p.showPage()
        p.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')

    def export_as_chargoon(self, request, queryset):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        prs_date_shift_list = []
        for i, obj in enumerate(queryset):
            prs_date_shift_id = str(getattr(obj, field_names[0]))
            prs_date_shift = PersonnelShiftDateAssignments.objects.get(pk=prs_date_shift_id)
            Personnel_id = getattr(prs_date_shift, 'Personnel_id')
            personnel = Personnel.objects.filter(id=Personnel_id)
            PersonnelBaseId = personnel[0].ExternalId
            year_period = getattr(prs_date_shift, 'YearWorkingPeriod')
            year_month = str(year_period // 100) + '/' + zero_pad(year_period % 100) + '/'
            for j, field in enumerate(field_names):
                if j > 3:
                    shift = Shifts.objects.filter(Title=str(getattr(obj, field)))
                    ShiftGuid = shift[0].ExternalGuid
                    Date = year_month + zero_pad(j - 3)
                    prs_date_shift_list.append([PersonnelBaseId, Date, ShiftGuid])

                    prs_date_shift_str = update_shift_async(PersonnelBaseId, Date, ShiftGuid)
                    prs_date_shift_str = str(PersonnelBaseId) + ' - ' + Date + ' - ' + ShiftGuid
                    p.drawString(10, 800 - ((i + 1) * (j + 1) * 10), prs_date_shift_str)
                    # break

        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='shift.pdf')

    actions = ["export_as_csv", "export_as_pdf", "export_as_chargoon"]

    export_as_csv.short_description = "خروجی اکسل"
    export_as_pdf.short_description = "گزارش pdf"
    export_as_chargoon.short_description = "تایید و ارسال به دیدگاه"


@admin.register(WorkSectionRequirements)
class WorkSectionRequirementsAdmin(admin.ModelAdmin):
    list_display = ('WorkSection', 'Year', 'Month', 'PersonnelTypeReq', 'ShiftType', 'ReqMinCount', 'ReqMaxCount',)
    list_filter = ('WorkSection__Hospital', 'WorkSection', 'Year', 'Month', 'ShiftType',)

    # def get_urls(self):
    #     urls = super().get_urls()
    #     extra_urls = [
    #         path("chart_data/", self.admin_site.admin_view(self.chart_data_endpoint))
    #     ]
    #     # NOTE! Our custom urls have to go before the default urls, because they
    #     # default ones match anything.
    #     return extra_urls + urls
    #
    #     # JSON endpoint for generating chart data that is used for dynamic loading
    #     # via JS.
    #
    # def chart_data_endpoint(self, request):
    #     chart_data = self.chart_data()
    #     return JsonResponse(list(chart_data), safe=False)
    #
    # def chart_data(self):
    #     return (
    #         WorkSectionRequirements.objects.annotate(PersonnelType='PersonnelTypeReq')
    #             .values("PersonnelType")
    #             .annotate(y=Count("id"))
    #             .order_by("-PersonnelType")
    #     )
    #
    # def changelist_view(self, request, extra_context=None):
    #     chart_data = self.chart_data()
    #     as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
    #     extra_context = extra_context or {"chart_data": as_json}
    #
    #     return super().changelist_view(request, extra_context=extra_context)


@admin.register(HardConstraints)
class HardConstraintsAdmin(admin.ModelAdmin):
    list_display = ('Personnel', 'YearWorkingPeriod', 'Day', 'ShiftType', 'Value')
    list_filter = ('Personnel__WorkSection__Hospital', 'Personnel__WorkSection', 'Personnel',
                   'YearWorkingPeriod', 'Day', 'ShiftType', 'Value')

