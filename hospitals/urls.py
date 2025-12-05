from django.urls import path
from . import views

urlpatterns = [
    
    path("login/", views.hospital_login, name="hospital_login"),
    path("logout/", views.hospital_logout, name="hospital_logout"),
    path("login/forgot-password/", views.hospital_forgot_password, name="hospital_forgot_password"),
    path("requests/all/", views.hospital_all_requests, name="hospital_all_requests"),
    path("dashboard/", views.hospital_dashboard, name="hospital_dashboard"),
    path("profile/edit/", views.hospital_profile_edit, name="hospital_profile_edit"),

    path("request/create/", views.hospital_request_create, name="hospital_request_create"),
    path(
        "request/<int:request_id>/",
        views.hospital_request_update,
        name="hospital_request_update",
    ),
    path(
        "request/<int:request_id>/delete/",
        views.hospital_request_delete,
        name="hospital_request_delete",
    ),

    path("signup/", views.hospital_signup, name="hospital_signup"),
    path("signup/success/", views.hospital_signup_success, name="hospital_signup_success"),


    path("requests/", views.public_blood_requests, name="public_blood_requests")

]
