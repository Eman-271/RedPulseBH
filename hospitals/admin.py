from django.contrib import admin
from .models import Hospital, Donor


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "hospital_type",
        "city_area",
        "email",
        "contact_name",
        "created_at",
    )
    list_filter = ("hospital_type", "city_area", "created_at")
    search_fields = (
        "name",
        "licence_number",
        "city_area",
        "email",
        "contact_name",
    )

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "blood_type",
        "city",
        "email",
        "phone",
        "created_at",
    )
    list_filter = ("blood_type", "city", "created_at")
    search_fields = ("full_name", "email", "phone", "cpr")