from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_request, name='login'),
    path('lawLogin', views.lawLogin, name='lawLogin'),
    path('FnLawFirmResetPassword', views.FnLawFirmResetPassword,
         name='FnLawFirmResetPassword'),
    path('FnExpertChangePassword', views.FnExpertChangePassword,
         name='FnExpertChangePassword'),
    path('FnExpertResetPassword', views.FnExpertResetPassword,
         name='FnExpertResetPassword'),
    path('expertLogin', views.expertLogin, name='expertLogin'),
    path('FnLawFirmChangePassword', views.FnLawFirmChangePassword,
         name='FnLawFirmChangePassword'),
]
