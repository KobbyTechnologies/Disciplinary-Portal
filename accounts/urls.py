from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_request, name='login'),
    path('lawLogin', views.lawLogin, name='lawLogin'),
    path('FnLawFirmChangePassword', views.FnLawFirmChangePassword,
         name='FnLawFirmChangePassword'),
    path('FnExpertChangePassword', views.FnExpertChangePassword,
         name='FnExpertChangePassword'),
]
