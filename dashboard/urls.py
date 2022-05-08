from django.urls import path
from . import views

urlpatterns = [
    path('dash', views.dashboard, name="dashboard"),
    path('caseDetails/<str:pk>', views.caseDetails, name="caseDetails"),
    path('caseAcceptance', views.FnExpertCaseAcceptance, name="CaseAcceptance"),
    path('expertComments/<str:pk>', views.FnExpertSaveComments,
         name="FnExpertSaveComments"),
    path('FnUploadAttachedDocument/<str:pk>', views.FnUploadAttachedDocument,
         name="FnUploadAttachedDocument"),
    path('FnExpertSubmitCase/<str:pk>', views.FnExpertSubmitCase,
         name="FnExpertSubmitCase"),

    path('lawDetails/<str:pk>', views.lawDetails, name="lawDetails"),
]
