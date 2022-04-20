from django.urls import path
from . import views

urlpatterns = [
    path('dash', views.dashboard, name="dashboard"),
    path('caseDetails', views.caseDetails, name="caseDetails"),
]
