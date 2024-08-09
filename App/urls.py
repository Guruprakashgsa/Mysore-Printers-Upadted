
from django.urls import path
from App.apis.api import *

urlpatterns = [
    path('login/', login, name="login"),
    path('admin-dashboard/', Admin_Dashboard, name="admin-dashboard"),
    path('lists/', lists, name="lists"),
    path('add/', Registration, name="registration"),
    path('user-edit-data/', user_edit_data, name="edit-data"),
    path('edit/', user_detail, name="edit"),
    path('delete/', user_detail, name="delete"),
    path('executivelists/', executivelists, name= "executivelists"),
    path("attendance/", location_list, name="attendancelists"),
    path("attendance-chart/", total_work_hours, name="attendance-chart"),
    path("collection-lists/" , admin_collection_list, name="admin-collection-lists"),
    path("data-upload/", upload_file, name="file-upload"),
    path("territory-data/", Territory_data_web, name="territory-data"),
    path('supply-report/', supply_report, name="supply-report"),
    path("admin-collection-data/", admin_collection_data, name= "admin_collection_data"),
    path("net-sale/", admin_netsales, name="netsale"),
    path("notification-view/", Notifications_web, name="notifications-web"),
    path("add-notification/", NotificationsFCMHTTP, name="add-notifications" ),
    path("lvd/", get_plant_edition, name="lvd"),
    path("profilesettingview/", ProfileSettingView, name="profileview"),
    path("profilesave/", ProfileSave, name="profilesave"),
    path("changepassword/", change_password, name="changepassword")
]
