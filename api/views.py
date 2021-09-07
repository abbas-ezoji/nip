from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes
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
            psd = nip.PersonnelShiftDateAssignmentsTabular.objects.filter(Shift__Length__gte=nooff,
                                                                          Personnel__id=p_id,
                                                                          YearWorkingPeriod__YearWorkingPeriod=yw_id,
                                                                          DayNo=day,
                                                                          PersonnelShiftDateAssignments__ShiftAssignment__Rank=rank)
        elif p_id and yw_id and day == 0:
            psd = nip.PersonnelShiftDateAssignmentsTabular.objects.filter(Shift__Length__gte=nooff,
                                                                          Personnel__id=p_id,
                                                                          YearWorkingPeriod__YearWorkingPeriod=yw_id,
                                                                          PersonnelShiftDateAssignments__ShiftAssignment__Rank=rank)
        elif p_id == 0 and worksection and yw_id and day:
            psd = nip.PersonnelShiftDateAssignmentsTabular.objects.filter(Shift__Length__gte=nooff,
                                                                          Personnel__WorkSection__id=worksection,
                                                                          YearWorkingPeriod__YearWorkingPeriod=yw_id,
                                                                          DayNo=day,
                                                                          PersonnelShiftDateAssignments__ShiftAssignment__Rank=rank)
        else:
            psd = nip.PersonnelShiftDateAssignmentsTabular.objects.filter(id=0)

        return psd
