from django.db import models
from django.core.validators import (
    RegexValidator,
    MinValueValidator,
    MaxValueValidator,
)


class Hospital(models.Model):
    HOSPITAL_TYPE_CHOICES = [
        ("government", "Government Hospital"),
        ("private", "Private Hospital"),
        ("clinic", "Clinic / Medical Center"),
        ("lab", "Diagnostic Lab"),
        ("other", "Other"),
    ]
    

    # Basic info
    name = models.CharField(max_length=255)

    hospital_type = models.CharField(
        max_length=20,
        choices=HOSPITAL_TYPE_CHOICES,
    )

    licence_number = models.CharField(
        max_length=8,
        db_index=True,  
        validators=[
            RegexValidator(
                r"^\d{8}$",
                "License / CR number must be exactly 8 digits.",
            )
        ],
        verbose_name="License / CR number",
    )

    # Location
    city_area = models.CharField(max_length=100)
    full_address = models.TextField()

    # Contact details
    phone = models.CharField(max_length=20)
    email = models.EmailField(
        unique=True,
        db_index=True,  
    )

    # Contact person
    contact_name = models.CharField(max_length=255)
    contact_role = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()

    # Login password 
    password = models.CharField(max_length=128)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Donor(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("prefer_not_to_say", "Prefer not to say"),
    ]

    BLOOD_TYPES = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("O+", "O+"), ("O-", "O-"),
        ("UNK", "Unknown"),
    ]

    # Personal details 
    full_name = models.CharField(max_length=255)

    cpr = models.CharField(
        max_length=9,
        unique=True,
        validators=[
            RegexValidator(
                r"^\d{9}$",
                "CPR / ID number must be exactly 9 digits.",
            )
        ],
        verbose_name="CPR / ID number",
    )

    age = models.PositiveIntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(65)]
    )

    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
    )

    # Contact info 
    city = models.CharField(max_length=100)

    # store only the 8 digits; "+973" is fixed in the UI
    phone = models.CharField(
        max_length=8,
        validators=[
            RegexValidator(
                r"^\d{8}$",
                "Mobile number must be 8 digits (without +973).",
            )
        ],
        verbose_name="Mobile number (without +973)",
    )

    email = models.EmailField(
        unique=True,
        db_index=True,  # for login and queries
    )

    # Blood & donation details 
    blood_type = models.CharField(
        max_length=3,
        choices=BLOOD_TYPES,
    )

    last_donation_date = models.DateField(
        null=True,
        blank=True,
    )

    health_notes = models.TextField(
        blank=True,
        help_text="Optional health conditions or notes for hospitals.",
    )

    # Login / account info 
    password = models.CharField(
        max_length=128,
        help_text="Store plain for now; later can be changed to hashed.",
    )

    #  Consents 
    contact_consent = models.BooleanField(
        default=False,
        help_text="Donor agrees that hospitals may contact them about requests.",
    )
    info_accuracy_confirmed = models.BooleanField(
        default=False,
        help_text="Donor confirms the information is accurate.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.blood_type})"

class BloodRequest(models.Model):
    URGENCY_CHOICES = [
        ("critical", "Critical"),
        ("high", "High"),
        ("normal", "Normal"),
    ]

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="blood_requests",
    )

    # e.g. "Salmaniya Medical Complex – Manama"
    title = models.CharField(max_length=255)

    city = models.CharField(max_length=100)

    # A+, O-, etc.
    blood_type_needed = models.CharField(max_length=3)

    units = models.PositiveIntegerField(default=1)

    urgency = models.CharField(
        max_length=10,
        choices=URGENCY_CHOICES,
        default="normal",
    )

    notes = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} – {self.blood_type_needed} ({self.city})"
    
