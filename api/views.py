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
        p_id = int(self.request.GET.get('id', 0))
        if p_id:
            psd = nip.PersonnelShiftDateAssignments.objects.all().filter(pk=p_id)
        else:
            psd = nip.PersonnelShiftDateAssignments.objects.all()

        return psd
