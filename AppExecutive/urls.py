from django.urls import path
from AppExecutive.api.api import *

urlpatterns = [
    path('working_summary/',working_summary, name='working_summary'),
    path('check_in/',  check_in, name='check_in'),
    path('check_out/', check_out, name='check_out'),
    path('collection_report/', collection_report, name='collection_report'),
    path('summary-report/', summary_Report, name='summary_report'),
    path('collection-list/', collection_list, name='collection_list'),
    path('supply-report-list/', supply_report_list, name='supply_report_list'),
    path('collection-data-web/', collection_data_web, name='collection_data_web'),
    path('daily-summary/', daily_summary, name='daily_summary'),
    path('executive_netsales/', executive_netsales, name='admin_netsales'),
    path('profile_setting/', ProfileSettingView, name='profile_setting'),
    path('profile_save/', ProfileSave, name='profile_save'),
]
