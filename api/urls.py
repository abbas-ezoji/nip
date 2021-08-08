from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path('personnel/', views.Personnel.as_view()),
    path('psd/', views.PersonnelShiftDateAssignments.as_view()),
    path('shifts_day_details/', views.ShiftDayDetails.as_view()),
]
