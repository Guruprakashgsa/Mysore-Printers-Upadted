from django.urls import path
from Agent.api.api import *

urlpatterns = [
    path('working-summary/', working_summary, name='working_summary'),
    path('check-in/', check_in, name='check_in'),
    path('check-out/', check_out, name='check_out'),
    path('summary-report/', summary_report, name='summary-report'),
    path('profile/', ProfileSettingView, name='profile_setting'),
    path("profilesave/", ProfileSave, name="profilesave"),
    
]
