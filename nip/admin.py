import csv
from django.utils.html import format_html
from django.contrib import admin
from .models import *

import io
from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.http import FileResponse
from reportlab.pdfgen import canvas


class WorkSectionAdmin(admin.ModelAdmin):
    list_display = ('Code', 'Title', 'ExternalId')
    list_filter = ('Code', 'Title')


class PersonnelTypesAdmin(admin.ModelAdmin):
    list_display = ('Code', 'Title')
    list_filter = ('Code', 'Title')


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


class ShiftAssignmentsAdmin(admin.ModelAdmin):
    list_display = ('WorkSection', 'YearWorkingPeriod', 'Rank', 'Cost', 'EndTime')
    list_filter = ('WorkSection', 'YearWorkingPeriod', 'Rank')
    inlines = [
        PersonnelShiftDateAssignmentsInline,
        ShiftConstDayRequirementsInline,
        ShiftConstPersonnelTimesInline,
    ]

    def get_ordering(self, request):
        return ['WorkSection', 'YearWorkingPeriod', 'Rank']


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


class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('YearWorkingPeriod', 'WorkSection', 'PersonnelBaseId', 'FullName',
                    'PersonnelTypes', 'RequirementWorkMins_esti', 'EfficiencyRolePoint')
    list_filter = ('YearWorkingPeriod', 'WorkSection', 'PersonnelBaseId', 'FullName',
                   'PersonnelTypes', 'RequirementWorkMins_esti', 'EfficiencyRolePoint')


class ShiftRecommendManagerAdmin(admin.ModelAdmin):
    list_display = ('YearWorkingPeriod', 'WorkSection', 'coh_const_DayRequirements', 'coh_const_PersonnelPerformanceTime',
                    'TaskStatus', 'RecommenderStatus', )
    list_filter = ('YearWorkingPeriod', 'WorkSection', 'TaskStatus', 'RecommenderStatus',)



class PersonnelShiftDateAssignmentsAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in PersonnelShiftDateAssignments._meta.get_fields()]
    list_display = ('shift_colored',)
    list_filter = ('ShiftAssignment__WorkSection', 'YearWorkingPeriod',
                   'ShiftAssignment__Rank',)

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
            year_period = getattr(prs_date_shift, 'YearWorkingPeriod')
            for j, field in enumerate(field_names):
                if j > 3:
                    shift = Shifts.objects.filter(Title=str(getattr(obj, field)))
                    shift_id = shift[0].Code
                    prs_date_shift_list.append([Personnel_id, year_period, j - 3, shift_id])

                    # prs_date_shift_str = str(Personnel_id)+'-' + str(year_period)+'-' + str(j-3)+'-' + str(shift_id)
                    # p.drawString(10, 800 - ((i+1)*(j+1) * 10), prs_date_shift_str)

        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='shift.pdf')

    actions = ["export_as_csv", "export_as_pdf", "export_as_chargoon"]

    export_as_csv.short_description = "خروجی اکسل"
    export_as_pdf.short_description = "گزارش pdf"
    export_as_chargoon.short_description = "تایید و ارسال به دیدگاه"


class WorkSectionRequirementsAdmin(admin.ModelAdmin):
    list_display = ('WorkSection', 'PersonnelTypeReq', 'ShiftType', 'ReqMinCount', 'ReqMaxCount',)
    list_filter = ('WorkSection', 'ShiftType__Title',)


class PersonnelLeavesAdmin(admin.ModelAdmin):
    list_display = ('Personnel', 'YearWorkingPeriod', 'Day', 'ExternalId')
    list_filter = ('Personnel__WorkSection', 'Personnel__FullName', 'YearWorkingPeriod', 'Day',)


admin.site.register(WorkSection, WorkSectionAdmin)
admin.site.register(PersonnelLeaves, PersonnelLeavesAdmin)
admin.site.register(WorkSectionRequirements, WorkSectionRequirementsAdmin)
admin.site.register(Shifts, ShiftsAdmin)
admin.site.register(Personnel, PersonnelAdmin)
admin.site.register(PersonnelTypes, PersonnelTypesAdmin)
admin.site.register(ShiftAssignments, ShiftAssignmentsAdmin)
admin.site.register(PersonnelShiftDateAssignments, PersonnelShiftDateAssignmentsAdmin)
admin.site.register(ShiftRecommendManager, ShiftRecommendManagerAdmin)
