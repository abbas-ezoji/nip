from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path('personnel/', views.Personnel.as_view()),
    path('psd/', views.PersonnelShiftDateAssignments.as_view()),
    path('shifts-day-details/', views.ShiftDayDetails.as_view()),
    path('self-declaration-initial/', views.SelfDeclarationInitial.as_view()),
    path('self-declaration-post/', views.SelfDeclarationPost.as_view()),
    path('self-declaration-get/', views.SelfDeclarationGet.as_view()),
    path('self-declaration-get-day-details/', views.SelfDeclarationGetDayDetails.as_view()),
    path('account/', include('api.account.urls')),
]
