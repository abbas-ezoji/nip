import random
import requests
import re
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .serializers import *
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from datetime import timedelta
from rest_framework import status


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


def validate_mobile(value):
    if len(value) != 11:
        return False
    rule = re.compile(r'^(?:\+?44)?[07]\d{9,13}$')
    return rule.search(value)


def send_sms(mobile, otp):
    url = "https://sms.magfa.com/api/http/sms/v2/send"
    headers = {'accept': "application/json", 'cache-control': "no-cache"}

    # credentials

    username = "radman_73510"
    password = "CPW71LVXaXSWUI3b"
    domain = "magfa"

    # or json data
    payload_json = {'senders': ['+98300073920'],
                    'messages': [f'iplanner Code is : {otp}'],
                    'recipients': [str(mobile)]}
    # call json
    res_msg = requests.post(url, headers=headers, auth=(username + '/' + domain, password), json=payload_json)

    return res_msg.json()


@api_view(['POST'])
def force_generate_otp(request):
    # if request.method == 'GET':
    #     mobile = request.GET.get('mobile', None)
    if request.method == 'POST':
        mobile = request.data.get('mobile', '-')

    if validate_mobile(mobile):
        otp = random.randint(11111, 99999)
        expired_date = (datetime.now() + timedelta(minutes=2)).replace(tzinfo=None)
        totp = datetime.now().replace(tzinfo=None)
        remaining_time = (expired_date - totp).seconds

        obj, created = User.objects.get_or_create(username=mobile)
        user = obj if obj else created
        new = True if created else False

        if new:
            customer = user_profile.Customer.objects.create(user=user, otp=otp, expired_date=expired_date,
                                                            mobile=mobile)
            customer.mobile = mobile
            customer.otp = otp
            customer.expired_date = expired_date
            customer.active = False
            customer.save()
            res_msg = send_sms(mobile, otp)

            if res_msg['status'] == 0:
                content = {'message': 'sms did sent',
                           'active': False,
                           'set_password': False,
                           'set_nickname': False,
                           'remaining': remaining_time}
                return Response(content, status=status.HTTP_200_OK)
            else:
                content = {'message': 'sms did not sent!!!'}
                return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            customer = user_profile.Customer.objects.get(user=user)
            expire = customer.expired_date.replace(tzinfo=None)
            set_password = True if user.password else False
            set_nickname = True if customer.nick_name else False
            active = True if customer.active else False

            if totp < expire:
                remaining_time = (expire - totp).seconds
                content = {'message': 'sms did sent before',
                           'active': active,
                           'set_password': set_password,
                           'set_nickname': set_nickname,
                           'remaining': remaining_time}
                return Response(content, status=status.HTTP_200_OK)

            res_msg = send_sms(mobile, otp)
            if res_msg['status'] == 0:
                customer.mobile = mobile
                customer.otp = otp
                customer.expired_date = expired_date
                customer.save()
                content = {'message': 'sms did sent',
                           'active': active,
                           'set_password': set_password,
                           'set_nickname': set_nickname,
                           'remaining': remaining_time}
                return Response(content, status=status.HTTP_200_OK)
            else:
                content = {'message': 'sms did not sent!!!'}
                return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        content = {'message': 'please enter mobile'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def generate_otp(request):
    # if request.method == 'GET':
    #     mobile = request.GET.get('mobile', None)
    if request.method == 'POST':
        mobile = request.data.get('mobile', None)

    if validate_mobile(mobile):
        otp = random.randint(11111, 99999)
        expired_date = (datetime.now() + timedelta(minutes=2)).replace(tzinfo=None)
        totp = datetime.now().replace(tzinfo=None)
        remaining_time = (expired_date - totp).seconds

        obj, created = User.objects.get_or_create(username=mobile)
        user = obj if obj else created
        new = True if created else False

        if new:
            customer = user_profile.Customer.objects.create(user=user, otp=otp, expired_date=expired_date,
                                                            mobile=mobile)
            customer.mobile = mobile
            customer.otp = otp
            customer.expired_date = expired_date
            customer.active = False
            customer.save()
            res_msg = send_sms(mobile, otp)

            if res_msg['status'] == 0:
                content = {'message': 'sms did sent',
                           'active': False,
                           'set_password': False,
                           'set_nickname': False,
                           'remaining': remaining_time}
                return Response(content, status=status.HTTP_200_OK)
            else:
                content = {'message': 'sms did not sent!!!'}
                return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            customer = user_profile.Customer.objects.get(user=user)
            expire = customer.expired_date.replace(tzinfo=None)
            set_password = True if user.password else False
            set_nickname = True if customer.nick_name else False
            active = True if customer.active else False

            if active:
                content = {'message': 'user is active',
                           'active': active,
                           'set_password': set_password,
                           'set_nickname': set_nickname,
                           }
                return Response(content, status=status.HTTP_200_OK)

            if totp < expire:
                remaining_time = (expire - totp).seconds
                content = {'message': 'sms did sent before',
                           'active': active,
                           'set_password': set_password,
                           'set_nickname': set_nickname,
                           'remaining': remaining_time}
                return Response(content, status=status.HTTP_200_OK)

            res_msg = send_sms(mobile, otp)
            if res_msg['status'] == 0:
                customer.mobile = mobile
                customer.otp = otp
                customer.expired_date = expired_date
                customer.save()
                content = {'message': 'sms did sent',
                           'active': active,
                           'set_password': set_password,
                           'set_nickname': set_nickname,
                           'remaining': remaining_time}
                return Response(content, status=status.HTTP_200_OK)
            else:
                content = {'message': 'sms did not sent!!!'}
                return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        content = {'message': 'please enter mobile'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def verify_otp(request):
    # mobile = request.GET.get('mobile', None)
    # request_otp = request.GET.get('otp', None)

    if request.method == 'POST':
        mobile = request.data.get('mobile', None)
        request_otp = request.data.get('otp', None)

    if mobile and request_otp:
        try:
            user = User.objects.get(username=mobile)
            customer = user_profile.Customer.objects.get(user=user)

        except User.DoesNotExist:
            content = {'message': 'please generate otp'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        totp = datetime.now().replace(tzinfo=None)

        expire = customer.expired_date.replace(tzinfo=None)

        if totp > expire:
            content = {'message': 'time is Expired'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        otp = customer.otp
        if otp != request_otp:
            content = {'message': 'Enter valid otp'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        token = Token.objects.get_or_create(user=user)
        customer.active = True
        customer.save()
        set_nickname = True if customer.nick_name else False
        return Response({'token': str(token[0]),
                         'set_nickname': set_nickname},
                        status=status.HTTP_200_OK)
    else:
        content = {'message': 'Enter mobile and otp'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


@permission_classes([IsAuthenticated])
class logout(APIView):

    def post(self, request, *args, **kwargs):
        print('user' + str(request.user))
        try:
            request.user.auth_token.delete()
        except:
            print('null')

        return Response(status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
class ChangePasswordView(APIView):

    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        pwd = request.data.get('password', None)

        if pwd:
            user = User.objects.get(id=user_id)
            user.password = make_password(pwd)
            user.save()

            content = {'message': 'Password set',
                       'user': user_id}
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {'message': 'password is required'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated, ])
class UserGet_old(generics.ListAPIView):
    queryset = prf.UserProfile.objects.all()
    serializer_class = SerializerProfile

    def get_queryset(self):
        user_id = self.request.user.id
        profile = prf.UserProfile.objects.filter(User=user_id)
        return profile


@permission_classes([IsAuthenticated, ])
class UserGet(generics.ListAPIView):
    queryset = bs.Personnel.objects.all()
    serializer_class = SerializerPersonnel

    def get_queryset(self):
        user_id = self.request.user.id
        personnel = bs.Personnel.objects.filter(User=user_id)
        print(personnel)
        return personnel


@permission_classes([IsAuthenticated])
class SetNickName(APIView):

    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        nickname = request.data.get('nickname', None)
        print(user_id, nickname)
        if nickname:
            customer = user_profile.Customer.objects.get(user=user_id)
            customer.nick_name = nickname
            customer.save()

            content = {'message': 'nickname is set',
                       'user': user_id}
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {'message': 'nickname is required'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
