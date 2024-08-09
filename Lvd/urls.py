from django.urls import path
from Lvd.api.api import app_user_login,Dashboard, check_in, check_out, plant_edition

urlpatterns = [
    path('dashboard/', Dashboard, name='working_summary'),
    path('check_in/', check_in, name='check_in'),
    path('check_out/', check_out, name='check_out'),
    path('plant_edition/', plant_edition, name='plant_edition'),
]
