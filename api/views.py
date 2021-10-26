from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes
from rest_framework import status
from django.shortcuts import get_object_or_404
from basic_information import models as basic_information
from . import serializers
from nip import models as nip
from etl import models as etl
from rest_framework.pagination import PageNumberPagination


@permission_classes([AllowAny, ])
class Personnel(generics.ListAPIView):
    queryset = basic_information.Personnel.objects.all()
    serializer_class = serializers.SerializerPersonnel

    def get_queryset(self):
        p_id = int(self.request.GET.get('id', 0))
        if p_id:
            personnel = basic_information.Personnel.objects.all().filter(pk=p_id)
        else:
            personnel = basic_information.Personnel.objects.all()

        return personnel


@permission_classes([AllowAny, ])
class PersonnelShiftDateAssignments(generics.ListAPIView):
    queryset = nip.PersonnelShiftDateAssignments.objects.all()
    serializer_class = serializers.SerializerPersonnelShiftDateAssignments

    def get_queryset(self):
        p_id = int(self.request.GET.get('p_id', 0))
        yw_id = int(self.request.GET.get('yw_id', 0))
        if p_id and yw_id:
            psd = nip.PersonnelShiftDateAssignments.objects.filter(Personnel=p_id,
                                                                   YearWorkingPeriod__YearWorkingPeriod=yw_id,
                                                                   ShiftAssignment__Rank=1)
        elif p_id and yw_id == 0:
            psd = nip.PersonnelShiftDateAssignments.objects.filter(Personnel=p_id,
                                                                   ShiftAssignment__Rank=1)
        else:
            psd = nip.PersonnelShiftDateAssignments.objects.all()

        return psd


@permission_classes([AllowAny, ])
class ShiftDayDetails(generics.ListAPIView):
    queryset = nip.PersonnelShiftDateAssignmentsTabular.objects.all()
    serializer_class = serializers.SerializerPersonnelShiftDateAssignmentsTabular

    def get_queryset(self):
        p_id = int(self.request.GET.get('p_id', 0))
        yw_id = int(self.request.GET.get('yw_id', 0))
        day = int(self.request.GET.get('day', 0))
        worksection = int(self.request.GET.get('worksection', 0))
        nooff = int(self.request.GET.get('nooff', 0))
        rank = int(self.request.GET.get('rank', 1))

        if p_id and yw_id and day:
            psd = nip.PersonnelShiftDateAssignmentsTabular.objects.filter(# Shift__Length__gte=nooff,
                                                                          Personnel__id=p_id,
                                                                          YearWorkingPeriod__YearWorkingPeriod=yw_id,
                                                                          DayNo=day,
                                                                          PersonnelShiftDateAssignments__ShiftAssignment__Rank=rank)
        elif p_id and yw_id and day == 0:
            print('p_id and yw_id and day == 0', p_id , yw_id , day, nooff, rank)
            psd = nip.PersonnelShiftDateAssignmentsTabular.objects.filter(# Shift__Length__gte=nooff,
                                                                          Personnel__id=p_id,
                                                                          YearWorkingPeriod__id=yw_id,
                                                                          PersonnelShiftDateAssignments__ShiftAssignment__Rank=rank)
            print(psd)
        elif p_id == 0 and worksection and yw_id and day:
            psd = nip.PersonnelShiftDateAssignmentsTabular.objects.filter(# Shift__Length__gte=nooff,
                                                                          Personnel__WorkSection__id=worksection,
                                                                          YearWorkingPeriod__YearWorkingPeriod=yw_id,
                                                                          DayNo=day,
                                                                          PersonnelShiftDateAssignments__ShiftAssignment__Rank=rank)
        else:
            psd = nip.PersonnelShiftDateAssignmentsTabular.objects.filter(id=0)

        return psd


@permission_classes([AllowAny, ])
class SelfDeclarationGet(generics.ListAPIView):
    queryset = nip.SelfDeclaration.objects.all()
    serializer_class = serializers.SerializerSelfDeclaration

    def get_queryset(self):
        p_id = int(self.request.GET.get('personnel_id', 0))
        year_working_period = int(self.request.GET.get('yearworkingperiod_id', 0))
        day = int(self.request.GET.get('day', 0))
        if p_id:
            work_section = nip.Personnel.objects.get(id=p_id).WorkSection.id
            print(work_section)
            self_dec = nip.SelfDeclaration.objects.filter(YearWorkingPeriod=year_working_period, Day=day,
                                                          Personnel__WorkSection=work_section)

        else:
            self_dec = nip.SelfDeclaration.objects.all()

        return self_dec


@permission_classes([AllowAny, ])
class SelfDeclarationGetDayDetails(generics.ListAPIView):
    queryset = nip.SelfDeclaration.objects.all()
    serializer_class = serializers.SerializerSelfDeclarationDayDetails

    def get_queryset(self):
        work_section = int(self.request.GET.get('worksection_id', 0))
        year_working_period = int(self.request.GET.get('yw_id', 0))
        day = int(self.request.GET.get('day', 0))
        print(work_section, year_working_period, day)
        self_dec = nip.SelfDeclaration.objects.filter(YearWorkingPeriod=year_working_period,
                                                      Day=day,
                                                      Personnel__WorkSection__id=work_section
                                                      )

        return self_dec



@permission_classes([AllowAny])
class SelfDeclarationPost(APIView):

    def post(self, request, *args, **kwargs):
        personnel_id = request.data.get('personnel_id', None)
        year_working_period_id = request.data.get('yearworkingperiod_id', None)
        day = request.data.get('day', None)
        shift_type_id = request.data.get('shift_type', None)
        value = request.data.get('value', None)

        personnel = nip.Personnel.objects.get(pk=personnel_id)
        YearWorkingPeriod = etl.YearWorkingPeriod.objects.get(pk=year_working_period_id)
        shift_type = basic_information.ShiftTypes.objects.get(pk=shift_type_id)
        print(personnel, YearWorkingPeriod, shift_type)

        self_dec = nip.SelfDeclaration.objects.filter(Personnel=personnel, YearWorkingPeriod=YearWorkingPeriod,
                                                      Day=day, ShiftType=shift_type)[0]
        print(self_dec)
        if personnel_id and year_working_period_id and day and shift_type and value:
            if self_dec:
                self_dec.Value = value
                self_dec.save()
            else:
                print('else')
                self_dec = nip.SelfDeclaration(Personnel=personnel, YearWorkingPeriod=YearWorkingPeriod,
                                               Day=day, ShiftType=shift_type, Value=value)
                self_dec.save()

            content = {'message': 'data set',
                       'self_dec': self_dec.id}

            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {'message': 'Fill all required fields'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
