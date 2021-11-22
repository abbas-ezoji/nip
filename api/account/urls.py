from django.urls import path
from django.conf.urls import url, include
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from django.urls import re_path


urlpatterns = [
    # re_path(r'register/?$', views.RegisterView.as_view(), name='auth_register'),
    path('generate-otp/', views.generate_otp, name='auth_generate_otp'),
    path('force-generate-otp/', views.force_generate_otp, name='auth_force_generate_otp'),
    re_path(r'verify-otp/?$', views.verify_otp, name='auth_verify_otp'),
    # re_path(r'login/?$', obtain_auth_token, name='auth_login'),
    re_path(r'login/?$', views.login.as_view(), name='simple_login'),
    re_path(r'set-password/?$', views.ChangePasswordView.as_view(), name='auth_change_password'),
    re_path(r'logout/?$', views.logout.as_view(), name='auth_logout'),
    # re_path(r'profile/?$', views.UserGet.as_view(), name='user_details'),
    re_path(r'profile/?$', views.SimpleUserGet.as_view(), name='user_details'),
    # re_path(r'set-nickname/?$', views.SetNickName.as_view(), name='set_nickname'),
]
