from django.urls import path
from django.urls import include
from . import views


urlpatterns = [
    path('personnel/', views.Personnel.as_view()),
]