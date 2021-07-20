from django.contrib.auth.models import User, Group
from rest_framework import serializers
from basic_information import models as basic_information
from nip import models as nip


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


# class SerializerPersonnelShiftDateAssignments(serializers.ModelSerializer):
#
#
# class SerializerShift(serializers.ModelSerializer):
#     home_sections = SerializerHomeSection(many=True)
#     promotions = SerializerPromotion(many=True)
#
#     class Meta:
#         model = basic_information.Home
#         fields = ['id', 'title', 'seo_title', 'meta_description', 'description', 'home_sections', 'promotions']
