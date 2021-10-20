from django.contrib.auth.models import User, Group
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator, ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from authentication import models as prf
from basic_information import models as bs
from etl import models as etl
from django.contrib.auth.hashers import make_password


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=False)
    new_password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', "username", 'email', 'first_name', 'last_name',)

    # turn text to hashed password
    def restore_object(self, attrs, instance=None):
        attrs['password'] = make_password(attrs['password'])
        return super(UserSerializer, self).restore_object(attrs, instance=None)


class SerializerHospital(serializers.ModelSerializer):

    class Meta:
        model = bs.Hospital
        fields = '__all__'


class SerializerWorkSection(serializers.ModelSerializer):
    Hospital = SerializerHospital(read_only=True)

    class Meta:
        model = bs.WorkSection
        fields = ['id', 'Hospital', 'Code', 'Title', ]


class SerializerYearWorkingPeriod(serializers.ModelSerializer):

    class Meta:
        model = etl.YearWorkingPeriod
        fields = ['id', 'YearWorkingPeriod', 'State', ]


class SerializerPersonnel(serializers.ModelSerializer):
    Hospital = SerializerHospital(read_only=True)
    WorkSection = SerializerWorkSection(read_only=True)
    User = UserSerializer(read_only=True)
    YearWorkingPeriod = SerializerYearWorkingPeriod(read_only=True)

    class Meta:
        model = bs.Personnel
        fields = ['id', 'PersonnelNo', 'YearWorkingPeriod', 'Hospital', 'WorkSection', 'FullName',
                  'PersonnelTypes', 'EfficiencyRolePoint', 'Active', 'User', ]


class SerializerProfile(serializers.ModelSerializer):
    User = UserSerializer(read_only=True)
    Hospital = SerializerHospital(read_only=True)
    WorkSection = SerializerWorkSection(read_only=True)
    # Personnel = SerializerPersonnel(read_only=True)

    class Meta:
        model = prf.UserProfile
        fields = ['id', 'User', 'Hospital', 'WorkSection', 'Level', 'PersonnelNo',
                  # 'Personnel',
                  ]


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('username',)

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
        )
        user.set_password('12345')
        user.save()

        return user



