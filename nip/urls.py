from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('model/<int:pk>', views.model, name='model'),
]
