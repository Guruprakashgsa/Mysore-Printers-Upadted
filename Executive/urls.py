from django.urls import path
from Executive.apis.api import *

urlpatterns = [
    path('executive_working_summary/', executive_working_summary, name='executive_working_summary'),
    path('list_locations_by_executive/', list_locations_by_executive, name='list_locations_by_executive'),
    path('collection_list/', collection_list, name='collection_list'),
    path('executive_collection_agent_report/', executive_collection_agent_report, name='executive_collection_agent_report'),
    path('executive_collection_territory_report/', executive_collection_territory_report, name='executive_collection_territory_report'),
    path('supply_report_list/', supply_report_list, name='supply_report_list'),
]
