from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.shortcuts import get_object_or_404
from basic_information import models as basic_information
from . import serializers
from nip import models as nip
from etl import models as etl
import json
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
    serializer_class = serializers.SerializerPersonnelShiftDateAssignmentsTabular_DayDetail

    def get_queryset(self):
        p_id = int(self.request.GET.get('p_id', 0))
        yw_id = int(self.request.GET.get('yw_id', 0))
        day = int(self.request.GET.get('day', 0))
        worksection = int(self.request.GET.get('worksection', 0))
        nooff = int(self.request.GET.get('nooff', 0))
        rank = int(self.request.GET.get('rank', 1))
        print(worksection, yw_id, day)
        psd = nip.PersonnelShiftDateAssignmentsTabular.objects.filter(Shift__Length__gte=nooff,
                                                                      Personnel__WorkSection__id=worksection,
                                                                      YearWorkingPeriod__id=yw_id,
                                                                      DayNo=day,
                                                                      PersonnelShiftDateAssignments__ShiftAssignment__Rank=rank)

        return psd


@permission_classes([AllowAny, ])
class ShiftPersonnelDetails(generics.ListAPIView):
    queryset = nip.PersonnelShiftDateAssignmentsTabular.objects.all()
    serializer_class = serializers.SerializerPersonnelShiftDateAssignmentsTabular_PersonnelDetails

    def get_queryset(self):
        p_id = int(self.request.GET.get('p_id', 0))
        yw_id = int(self.request.GET.get('yw_id', 0))
        day = int(self.request.GET.get('day', 0))
        worksection = int(self.request.GET.get('worksection', 0))
        nooff = int(self.request.GET.get('nooff', 0))
        rank = int(self.request.GET.get('rank', 1))
        print(p_id, yw_id)
        psd = nip.PersonnelShiftDateAssignmentsTabular.objects.filter(Shift__Length__gte=nooff,
                                                                      Personnel__id=p_id,
                                                                      YearWorkingPeriod__id=yw_id,
                                                                      PersonnelShiftDateAssignments__ShiftAssignment__Rank=rank)

        return psd


@permission_classes([AllowAny, ])
class ShiftPersonnelDetails_ByID(generics.ListAPIView):
    queryset = nip.PersonnelShiftDateAssignmentsTabular.objects.all()
    serializer_class = serializers.SerializerPersonnelShiftDateAssignmentsTabular_PersonnelDetails

    def get_queryset(self):
        shift_assignment_id = int(self.request.GET.get('shiftassignment', 0))
        personnel_id = int(self.request.GET.get('personnel', 0))

        psd = nip.PersonnelShiftDateAssignmentsTabular. \
            objects.filter(PersonnelShiftDateAssignments__ShiftAssignment__id=shift_assignment_id,
                           Personnel__id=personnel_id).order_by('DayNo')

        return psd


@permission_classes([AllowAny, ])
class ShiftAssignment(generics.ListAPIView):
    queryset = nip.ShiftAssignments.objects.all()
    serializer_class = serializers.SerializerShiftAssignmentsDetails

    def get_queryset(self):
        p_id = int(self.request.GET.get('p_id', 0))
        yw_id = int(self.request.GET.get('yw_id', 0))
        nooff = int(self.request.GET.get('nooff', 0))
        rank = int(self.request.GET.get('rank', 0))
        print(p_id, yw_id)
        personnel = basic_information.Personnel.objects.get(pk=p_id)
        worksection = personnel.WorkSection
        if rank:
            shift_ass = nip.ShiftAssignments.objects.filter(WorkSection=worksection,
                                                            YearWorkingPeriod__id=yw_id,
                                                            Rank=rank).order_by('Rank')
        else:
            shift_ass = nip.ShiftAssignments.objects.filter(WorkSection=worksection,
                                                            YearWorkingPeriod__id=yw_id).order_by('Rank')

        return shift_ass


@permission_classes([AllowAny, ])
class SelfDeclarationGet(generics.ListAPIView):
    queryset = nip.SelfDeclaration.objects.all()
    serializer_class = serializers.SerializerSelfDeclaration

    def get_queryset(self):
        p_id = int(self.request.GET.get('personnel_id', 0))
        year_working_period = int(self.request.GET.get('yw_id', 0))
        # day = int(self.request.GET.get('day', 0))
        self_dec = nip.SelfDeclaration.objects.filter(YearWorkingPeriod=year_working_period,
                                                      Personnel__id=p_id)
        return self_dec


@permission_classes([AllowAny, ])
class SelfDeclarationGetDayDetails(generics.ListAPIView):
    queryset = nip.SelfDeclaration.objects.all()
    serializer_class = serializers.SerializerSelfDeclarationDayDetails

    def get_queryset(self):
        work_section = int(self.request.GET.get('worksection_id', 0))
        year_working_period = int(self.request.GET.get('yw_id', 0))
        day = int(self.request.GET.get('day', 0))
        shift_type = int(self.request.GET.get('shift_type', 0))
        print(work_section, year_working_period, day, shift_type)
        self_dec = nip.SelfDeclaration.objects.filter(YearWorkingPeriod__id=year_working_period,
                                                      Day=day,
                                                      Personnel__WorkSection__id=work_section,
                                                      ShiftType__Code=shift_type
                                                      )

        return self_dec


@permission_classes([AllowAny])
class SelfDeclarationPost(APIView):

    def post(self, request, *args, **kwargs):
        all_data = request.data
        data_count = 0
        for i, data in enumerate(all_data):
            personnel_id = data.get('Personnel', None)
            year_working_period_id = data.get('YearWorkingPeriod', None)
            day = data.get('Day', None)
            shift_type_code = data.get('ShiftTypeCode', None)
            value = data.get('Value', None)

            print(personnel_id, year_working_period_id, shift_type_code)
            personnel = nip.Personnel.objects.get(pk=personnel_id)
            YearWorkingPeriod = etl.YearWorkingPeriod.objects.get(pk=year_working_period_id)
            shift_type = basic_information.ShiftTypes.objects.get(Code=shift_type_code)
            print(personnel, YearWorkingPeriod, shift_type)

            self_dec = nip.SelfDeclaration.objects.filter(Personnel=personnel, YearWorkingPeriod=YearWorkingPeriod,
                                                          Day=day, ShiftType=shift_type)
            self_dec = self_dec[0] if self_dec else self_dec
            print(self_dec)
            if personnel_id and year_working_period_id and day and shift_type:
                if self_dec:
                    if value == 0:
                        self_dec.delete()
                    else:
                        self_dec.Value = value
                        self_dec.save()
                else:
                    if value:
                        print('else')
                        self_dec = nip.SelfDeclaration(Personnel=personnel, YearWorkingPeriod=YearWorkingPeriod,
                                                       Day=day, ShiftType=shift_type, Value=value)
                        self_dec.save()

                # return Response(content, status=status.HTTP_200_OK)
            else:
                content = {'message': 'Fill all required fields'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        data_count = i + 1
        content = {'message': f'all {data_count} data is success'}

        return Response(content, status=status.HTTP_200_OK)


@permission_classes([AllowAny])
class SelfDeclarationInitial(generics.ListAPIView):
    queryset = basic_information.Dim_Date.objects.all()
    serializer_class = serializers.SerializerDate

    def get_queryset(self):
        # user_id = request.user.id
        personnel_id = self.request.GET.get('personnel_id', None)
        yw = etl.YearWorkingPeriod.objects.get(State=1)
        print(yw)
        dates = basic_information.Dim_Date.objects.filter(YearWorkingPeriod=yw)

        return dates


@permission_classes([AllowAny])
class PersonnelShiftAssignmentPointsPost(APIView):

    def post(self, request, *args, **kwargs):
        personnel_id = request.data.get('Personnel', None)
        shift_assignment_id = request.data.get('ShiftAssignment', None)
        liked = request.data.get('Liked', 0)
        rank = request.data.get('Rank', 0)
        point = request.data.get('Point', 0)

        print(personnel_id, shift_assignment_id, rank, point)
        personnel = nip.Personnel.objects.get(pk=personnel_id)
        shift_assignment = nip.ShiftAssignments.objects.get(pk=shift_assignment_id)
        print(personnel, shift_assignment)

        personnel_shift_point = nip.PersonnelShiftAssignmentPoints.objects.filter(Personnel=personnel,
                                                                                  ShiftAssignment=shift_assignment)
        personnel_shift_point = personnel_shift_point[0] if personnel_shift_point else personnel_shift_point
        print(personnel_shift_point)

        if personnel_shift_point:
            if rank == 0 and point == 0 and liked == 0:
                personnel_shift_point.delete()
            else:
                personnel_shift_point.Rank = rank
                personnel_shift_point.Point = point
                personnel_shift_point.save()
        else:
            if rank or point:
                print('else')
                personnel_shift_point = nip.PersonnelShiftAssignmentPoints(Personnel=personnel,
                                                                           ShiftAssignment=shift_assignment,
                                                                           Liked=liked, Rank=rank, Point=point)
                personnel_shift_point.save()
            else:
                content = {'message': 'Fill all required fields'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        content = {'message': 'set data is success'}

        return Response(content, status=status.HTTP_200_OK)


@permission_classes([AllowAny])
class PersonnelShiftAssignmentPointsGet(generics.ListAPIView):
    queryset = nip.PersonnelShiftAssignmentPoints.objects.all()
    serializer_class = serializers.SerializerPersonnelShiftAssignmentPoints

    def get_queryset(self):
        # user_id = request.user.id
        personnel_id = self.request.GET.get('personnel', None)
        shift_assignment_id = self.request.GET.get('shiftAssignment', None)

        point_shift_assignment = nip.PersonnelShiftAssignmentPoints.objects.filter(ShiftAssignment__id=shift_assignment_id,
                                                                                   Personnel__id=personnel_id)

        return point_shift_assignment
