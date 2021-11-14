from django.contrib.auth.models import User, Group
from rest_framework import serializers
from basic_information import models as basic_information
from nip import models as nip
from etl import models as etl


class SerializerYearWorkingPeriod(serializers.ModelSerializer):
    class Meta:
        model = etl.YearWorkingPeriod
        fields = ['id', 'YearWorkingPeriod', 'State']


class SerializerDate(serializers.ModelSerializer):
    # YearWorkingPeriod = SerializerYearWorkingPeriod(read_only=True)

    class Meta:
        model = basic_information.Dim_Date
        fields = ['Day', 'Date', 'PersianDate', 'SpecialDay', 'YearWorkingPeriod', 'PersianWeekDayTitle']


class SerializerHospital(serializers.ModelSerializer):
    class Meta:
        model = basic_information.Hospital
        fields = ['id', 'Title']


class SerializerWorkSection(serializers.ModelSerializer):
    Hospital = SerializerHospital(read_only=True)

    class Meta:
        model = basic_information.WorkSection
        fields = ['id', 'Code', 'Title', 'Hospital']


class SerializerPersonnel(serializers.ModelSerializer):
    WorkSection = SerializerWorkSection(read_only=True)

    class Meta:
        model = basic_information.Personnel
        fields = ['id', 'PersonnelNo', 'FullName', 'WorkSection']


class SerializerShift(serializers.ModelSerializer):
    class Meta:
        model = basic_information.Shifts
        fields = ['id', 'Code', 'Type', 'Title']


class SerializerYearWorkingPeriod(serializers.ModelSerializer):
    class Meta:
        model = etl.YearWorkingPeriod
        fields = ['id', 'YearWorkingPeriod', 'State']


class SerializerShiftAssignments(serializers.ModelSerializer):
    class Meta:
        model = nip.ShiftAssignments
        fields = ['id', 'Rank']


class SerializerPersonnelShiftDateAssignments(serializers.ModelSerializer):
    ShiftAssignment = SerializerShiftAssignments(read_only=True)
    Personnel = SerializerPersonnel(read_only=True)
    YearWorkingPeriod = SerializerYearWorkingPeriod(read_only=True)
    D01 = SerializerShift(read_only=True)
    D02 = SerializerShift(read_only=True)
    D03 = SerializerShift(read_only=True)
    D04 = SerializerShift(read_only=True)
    D05 = SerializerShift(read_only=True)
    D06 = SerializerShift(read_only=True)
    D07 = SerializerShift(read_only=True)
    D08 = SerializerShift(read_only=True)
    D09 = SerializerShift(read_only=True)
    D10 = SerializerShift(read_only=True)
    D11 = SerializerShift(read_only=True)
    D12 = SerializerShift(read_only=True)
    D13 = SerializerShift(read_only=True)
    D14 = SerializerShift(read_only=True)
    D15 = SerializerShift(read_only=True)
    D16 = SerializerShift(read_only=True)
    D17 = SerializerShift(read_only=True)
    D18 = SerializerShift(read_only=True)
    D19 = SerializerShift(read_only=True)
    D20 = SerializerShift(read_only=True)
    D21 = SerializerShift(read_only=True)
    D22 = SerializerShift(read_only=True)
    D23 = SerializerShift(read_only=True)
    D24 = SerializerShift(read_only=True)
    D25 = SerializerShift(read_only=True)
    D26 = SerializerShift(read_only=True)
    D27 = SerializerShift(read_only=True)
    D28 = SerializerShift(read_only=True)
    D29 = SerializerShift(read_only=True)
    D30 = SerializerShift(read_only=True)
    D31 = SerializerShift(read_only=True)

    class Meta:
        model = nip.PersonnelShiftDateAssignments
        fields = '__all__'


class SerializerShiftLight(serializers.ModelSerializer):

    class Meta:
        model = basic_information.Shifts
        fields = ['id', 'Type', 'Title']


class SerializerPersonnelLight(serializers.ModelSerializer):
    class Meta:
        model = basic_information.Personnel
        fields = ['id', 'FullName', 'PersonnelNo', 'PersonnelTypes']


class SerializerPersonnelShiftDateAssignmentsTabular_DayDetail(serializers.ModelSerializer):
    Personnel = SerializerPersonnelLight(read_only=True)
    Shift = SerializerShiftLight(read_only=True)

    class Meta:
        model = nip.PersonnelShiftDateAssignmentsTabular
        fields = ['Date', 'DayNo', 'Personnel', 'Shift']


class SerializerPersonnelShiftDateAssignmentsTabular_PersonnelDetails(serializers.ModelSerializer):
    Shift = SerializerShiftLight(read_only=True)
    ShiftAssignment = SerializerShiftAssignments(read_only=True)

    class Meta:
        model = nip.PersonnelShiftDateAssignmentsTabular
        fields = ['ShiftAssignment', 'Date', 'DayNo', 'Shift', 'PersianDate', 'SpecialDay', 'PersianWeekDayTitle', ]


class SerializerShiftType(serializers.ModelSerializer):

    class Meta:
        model = basic_information.ShiftTypes
        fields = ['Code', 'Title']


class SerializerSelfDeclaration(serializers.ModelSerializer):
    # ShiftType = SerializerShiftType(read_only=True)

    class Meta:
        model = nip.SelfDeclaration
        fields = ['Personnel', 'YearWorkingPeriod', 'Day', 'ShiftTypeCode', 'Value']


class SerializerSelfDeclarationDayDetails(serializers.ModelSerializer):
    Personnel = SerializerPersonnelLight(read_only=True)
    ShiftType = SerializerShiftType(read_only=True)

    class Meta:
        model = nip.SelfDeclaration
        fields = '__all__'


class SerializerPersonnelShiftAssignmentPoints(serializers.ModelSerializer):
    Personnel = SerializerPersonnelLight(read_only=True)
    ShiftType = SerializerShiftAssignments(read_only=True)

    class Meta:
        model = nip.PersonnelShiftAssignmentPoints
        fields = '__all__'