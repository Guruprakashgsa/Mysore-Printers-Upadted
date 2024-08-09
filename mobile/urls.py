from mobile.api.api import *
from django.urls import path

urlpatterns = [
    path("login/", app_user_login, name="login")
]