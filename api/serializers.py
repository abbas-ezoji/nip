from django.contrib.auth.models import User, Group
from rest_framework import serializers
from basic_information import models as basic_information
from nip import models as nip


class SerializerPersonnel(serializers.ModelSerializer):

    class Meta:
        model = basic_information.Personnel
        fields = ['PersonnelNo', 'FullName']


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
