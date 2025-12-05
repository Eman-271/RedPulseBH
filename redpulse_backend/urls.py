"""
URL configuration for redpulse_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from hospitals import views as hospital_views


admin.site.site_header = "RedPulseBH Administration"
admin.site.site_title = "RedPulse Admin"
admin.site.index_title = "Welcome to RedPulseBH Admin Panel"

urlpatterns = [
   
    path("", hospital_views.home, name="home"),
    
     path("", include("hospitals.urls")),
     
    path("admin/", admin.site.urls),

    path("hospitals/", include("hospitals.urls")),

    path("donors/signup/", hospital_views.donor_signup, name="donor_signup"),
    path("donors/signup/success/", hospital_views.donor_signup_success, name="donor_signup_success"),
    path("donors/login/", hospital_views.donor_login, name="donor_login"),
    path("donors/dashboard/", hospital_views.donor_dashboard, name="donor_dashboard"),
    
     path("donors/profile/edit/", hospital_views.donor_profile_edit, name="donor_profile_edit"),
    path("donors/logout/", hospital_views.donor_logout, name="donor_logout"),
     path("donor/forgot-password/", hospital_views.donor_forgot_password, name="donor_forgot_password"),
    
    path(
        "donors/requests/<int:request_id>/decision/",
        hospital_views.donor_request_decision,
        name="donor_request_decision",
    ),
]
