from datetime import datetime
import re

from django.utils import timezone
from django.db import IntegrityError, DatabaseError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Hospital, BloodRequest, Donor 
from django.conf import settings
from pymongo import MongoClient
# Constant: validation pattern for 8-digit licence / CR
LICENCE_REGEX = re.compile(r"^\d{8}$")


# HOME / PUBLIC
def home(request):
    """
    Public home page.
    Shows the hero section, one urgent request, and top-level stats.
    """
    # total donors in the system
    registered_donors = Donor.objects.count()

    urgent_request = None
    fulfilled_requests = 0
    partner_facilities = 0

    # total number of hospitals / facilities
    try:
        partner_facilities = Hospital.objects.count()
    except DatabaseError:
        partner_facilities = 0

    
    try:
        all_requests = list(
            BloodRequest.objects.order_by("-created_at")
        )
    except DatabaseError:
        all_requests = []

    # the latest active request as the urgent one
    for req in all_requests:
        if getattr(req, "is_active", True):
            urgent_request = req
            break

    # count how many requests are closed (fulfilled)
    for req in all_requests:
        is_active_value = getattr(req, "is_active", True)
        if not bool(is_active_value):
            fulfilled_requests += 1

    context = {
        "registered_donors": registered_donors,
        "urgent_request": urgent_request,
        "fulfilled_requests": fulfilled_requests,
        "partner_facilities": partner_facilities,
    }
    return render(request, "index.html", context)


def public_blood_requests(request):
    """
    Public page that shows all active blood requests.
    We read all rows from MongoDB and filter in Python
    instead of using is_active=True in the query.
    """
    all_requests = []

    try:
        qs = BloodRequest.objects.all()
        all_requests = list(qs)
        print("DEBUG public_blood_requests total from DB:", len(all_requests))
    except DatabaseError as e:
        # log the error type for debugging
        print("DEBUG public_blood_requests error type:", type(e))
        print("DEBUG public_blood_requests error repr:", repr(e))
        all_requests = []

    # keep only requests where is_active is True
    active_requests = []
    for r in all_requests:
        # if some old records do not have is_active, treat them as active
        is_active_value = getattr(r, "is_active", True)
        if bool(is_active_value):
            active_requests.append(r)

    # order by created_at (newest first)
    now = timezone.now()
    active_requests.sort(
        key=lambda r: (r.created_at or now),
        reverse=True,
    )

    print("DEBUG public_blood_requests active after filter:", len(active_requests))

    return render(
        request,
        "public/public_blood_requests.html",
        {"active_requests": active_requests},
    )


# HOSPITAL REGISTRATION
def hospital_signup(request):
    """
    Simple hospital sign up form.
    Saves a new Hospital row if the data is valid.
    """
    if request.method == "POST":
        # read form values
        name = request.POST.get("name", "").strip()
        hospital_type = request.POST.get("hospital_type", "").strip()
        licence_number = request.POST.get("licence_number", "").strip()

        city_area = request.POST.get("city_area", "").strip()
        full_address = request.POST.get("full_address", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()

        contact_name = request.POST.get("contact_name", "").strip()
        contact_role = request.POST.get("contact_role", "").strip()
        contact_phone = request.POST.get("contact_phone", "").strip()
        contact_email = request.POST.get("contact_email", "").strip()

        password = request.POST.get("password", "").strip()

        errors = {}

        # validate licence / CR number
        if not licence_number:
            errors["licence_number"] = "License / CR number is required."
        elif not LICENCE_REGEX.match(licence_number):
            errors["licence_number"] = (
                "Please enter a valid License / CR number (exactly 8 digits)."
            )

        # hospital type must be selected
        if not hospital_type:
            errors["hospital_type"] = "Please select the hospital type."

        if errors:
            return render(
                request,
                "hospitals/hospital_signup.html",
                {"errors": errors, "form_data": request.POST},
            )

        # try to create hospital record
        try:
            Hospital.objects.create(
                name=name,
                hospital_type=hospital_type,
                licence_number=licence_number,
                city_area=city_area,
                full_address=full_address,
                phone=phone,
                email=email,
                contact_name=contact_name,
                contact_role=contact_role,
                contact_phone=contact_phone,
                contact_email=contact_email,
                password=password,
            )
        except IntegrityError:
            errors["email"] = (
                "A hospital with this email or licence number already exists."
            )
            return render(
                request,
                "hospitals/hospital_signup.html",
                {"errors": errors, "form_data": request.POST},
            )

        return redirect("hospital_signup_success")

    # GET request – empty form
    return render(request, "hospitals/hospital_signup.html")


def hospital_signup_success(request):
    """
    Simple success page after hospital sign up.
    """
    return render(request, "hospitals/hospital_signup_success.html")


# BASIC CRUD FOR HOSPITALS
def hospital_list(request):
    """
    Admin-style list of all hospitals.
    """
    hospitals = Hospital.objects.all().order_by("name")
    return render(request, "hospitals/hospital_list.html", {"hospitals": hospitals})


def hospital_update(request, pk):
    """
    Admin-style edit for an existing hospital (by pk).
    """
    hospital = get_object_or_404(Hospital, pk=pk)

    if request.method == "POST":
        hospital.name = request.POST.get("name", "").strip()
        hospital.hospital_type = request.POST.get("hospital_type", "").strip()
        hospital.licence_number = request.POST.get("licence_number", "").strip()
        hospital.city_area = request.POST.get("city_area", "").strip()
        hospital.full_address = request.POST.get("full_address", "").strip()
        hospital.phone = request.POST.get("phone", "").strip()
        hospital.email = request.POST.get("email", "").strip()
        hospital.contact_name = request.POST.get("contact_name", "").strip()
        hospital.contact_role = request.POST.get("contact_role", "").strip()
        hospital.contact_phone = request.POST.get("contact_phone", "").strip()
        hospital.contact_email = request.POST.get("contact_email", "").strip()
        hospital.save()

        return redirect("hospital_list")

    return render(request, "hospitals/hospital_update.html", {"hospital": hospital})


def hospital_delete(request, pk):
    """
    Admin-style delete for a hospital.
    """
    hospital = get_object_or_404(Hospital, pk=pk)

    if request.method == "POST":
        hospital.delete()
        return redirect("hospital_list")

    return render(request, "hospitals/hospital_delete.html", {"hospital": hospital})


# HOSPITAL LOGIN / LOGOUT / DASHBOARD
def hospital_login(request):
    """
    Hospital login with simple Remember Me.
    """

    
    if request.method == "GET" and request.session.get("hospital_id"):
        print("HOSPITAL already logged in, redirect to dashboard")
        return redirect("hospital_dashboard")

    error = None
    form_data = {}

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()
        form_data["email"] = email

        hospital = None
        try:
            hospital = Hospital.objects.get(email__iexact=email)
        except Hospital.DoesNotExist:
            error = "Incorrect email or password."

        if hospital and hospital.password != password:
            error = "Incorrect email or password."

        if error:
            return render(
                request,
                "hospitals/hospital_login.html",
                {"error": error, "form_data": form_data},
            )

        
        request.session["hospital_id"] = str(hospital.pk)
        request.session["hospital_name"] = hospital.name

        remember = request.POST.get("remember_me")
        print("HOSPITAL REMEMBER VALUE:", remember)

        if remember:
            #The session lasts for 7 days.
            request.session.set_expiry(7 * 24 * 60 * 60)
        else:
            #The session lasts for 2 hours.
            request.session.set_expiry(2 * 60 * 60)

        print("HOSPITAL SESSION EXPIRY (seconds):", request.session.get_expiry_age())

        return redirect("hospital_dashboard")

     
    return render(
        request,
        "hospitals/hospital_login.html",
        {"error": "", "form_data": {}},
    )

def hospital_forgot_password(request):
    """
    Simple password reset for hospitals:
    - User enters email + new password + confirm password.
    - If email exists and passwords match, update hospital.password.
    """
    error = None

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        new_password = request.POST.get("new_password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        if not email or not new_password or not confirm_password:
            error = "Please fill in all fields."
        elif new_password != confirm_password:
            error = "Passwords do not match."
        else:
            try:
                hospital = Hospital.objects.get(email__iexact=email)
                hospital.password = new_password
                hospital.save()
                return redirect("hospital_login")
            except Hospital.DoesNotExist:
                error = "No hospital found with this email."

    return render(
        request,
        "hospitals/hospital_forgot_password.html",
        {"error": error},
    )



def hospital_dashboard(request):
    """
    Main hospital dashboard.
    Shows facility info, recent blood requests, and basic stats.
    """
    hospital_id = request.session.get("hospital_id")
    if not hospital_id:
        return redirect("hospital_login")

    hospital = get_object_or_404(Hospital, pk=hospital_id)

    # recent requests list for this hospital
    try:
        blood_requests = (
            BloodRequest.objects
            .filter(hospital=hospital)
            .order_by("-created_at")[:10]
        )
    except DatabaseError as e:
        print("DEBUG hospital_dashboard list error:", e)
        blood_requests = []

    # simple statistics based on is_active flag
    base_qs = BloodRequest.objects.filter(hospital=hospital)

    try:
        open_count = base_qs.filter(is_active=True).count()
        closed_count = base_qs.filter(is_active=False).count()
        ongoing_count = 0  
    except DatabaseError as e:
        print("DEBUG hospital_dashboard stats error:", e)
        try:
            total = base_qs.count()
        except DatabaseError:
            total = 0
        open_count = total
        closed_count = 0
        ongoing_count = 0

    request_stats = {
        "open": open_count,
        "ongoing": ongoing_count,
        "closed": closed_count,
    }

   
    registered_donors = Donor.objects.count()

    context = {
        "hospital": hospital,
        "blood_requests": blood_requests,
        "request_stats": request_stats,
        "registered_donors": registered_donors,
    }
    return render(request, "hospitals/hospital_dashboard.html", context)


def hospital_logout(request):
    """
    Logs out the current hospital user by clearing the whole session.
    """
    request.session.flush()
    return redirect("hospital_login")


def hospital_all_requests(request):
    """
    Page inside the hospital portal that shows all blood requests
    (both open and closed) for the logged-in hospital.
    """
    hospital_id = request.session.get("hospital_id")
    if not hospital_id:
        return redirect("hospital_login")

    hospital = get_object_or_404(Hospital, pk=hospital_id)

    try:
        blood_requests = (
            BloodRequest.objects
            .filter(hospital=hospital)
            .order_by("-created_at")
        )
    except DatabaseError as e:
        print("DEBUG hospital_all_requests error:", e)
        blood_requests = []

    context = {
        "hospital": hospital,
        "blood_requests": blood_requests,
    }
    return render(request, "hospitals/hospital_all_requests.html", context)


# HOSPITAL PROFILE (SELF-SERVICE)
def hospital_profile_edit(request):
    """
    Allow the logged-in hospital to edit its own profile
    (name, type, address, contacts, etc.).
    """
    hospital_id = request.session.get("hospital_id")
    if not hospital_id:
        return redirect("hospital_login")

    hospital = get_object_or_404(Hospital, pk=hospital_id)

    if request.method == "POST":
        hospital.name = request.POST.get("name", "").strip()
        hospital.hospital_type = request.POST.get("hospital_type", "").strip()
        hospital.city_area = request.POST.get("city_area", "").strip()
        hospital.full_address = request.POST.get("full_address", "").strip()
        hospital.phone = request.POST.get("phone", "").strip()
        hospital.email = request.POST.get("email", "").strip()
        hospital.contact_name = request.POST.get("contact_name", "").strip()
        hospital.contact_role = request.POST.get("contact_role", "").strip()
        hospital.contact_email = request.POST.get("contact_email", "").strip()
        hospital.save()

        return redirect("hospital_dashboard")

    return render(
        request,
        "hospitals/hospital_profile_edit.html",
        {"hospital": hospital},
    )


# CREATE NEW BLOOD REQUEST (HOSPITAL)
def hospital_request_create(request):
    """
    Create a new BloodRequest for the logged-in hospital
    and then redirect back to the dashboard.
    """
    hospital_id = request.session.get("hospital_id")
    if not hospital_id:
        return redirect("hospital_login")

    hospital = get_object_or_404(Hospital, pk=hospital_id)

   
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        department = request.POST.get("department", "").strip()
        case_id = request.POST.get("case_id", "").strip()
        blood_type = request.POST.get("blood_type", "").strip()
        units_str = request.POST.get("units", "").strip()
        urgency = request.POST.get("urgency", "Normal").strip()
        notes = request.POST.get("notes", "").strip()

        errors = {}
        form_data = request.POST.copy()

        if not title:
            errors["title"] = "Request title is required."
        if not blood_type:
            errors["blood_type"] = "Blood type is required."

        
        units = None
        if units_str:
            try:
                units = int(units_str)
            except ValueError:
                errors["units"] = "Please enter a valid number of units."

        if errors:
            return render(
                request,
                "hospitals/hospital_request_form.html",
                {
                    "hospital": hospital,
                    "errors": errors,
                    "form_data": form_data,
                    "blood_types": blood_types,
                },
            )

        # build extra info into the notes field (department / case id)
        extra_info = []
        if department:
            extra_info.append(f"Department: {department}")
        if case_id:
            extra_info.append(f"Case ID: {case_id}")
        if extra_info:
            notes = (notes + "\n\n" if notes else "") + " | ".join(extra_info)

        # create the new blood request
        BloodRequest.objects.create(
            hospital=hospital,
            title=title,
            city=hospital.city_area,
            blood_type_needed=blood_type,
            units=units or 1,
            urgency=urgency,
            notes=notes,
            is_active=True,
        )

        return redirect("hospital_dashboard")

    # GET – show empty form
    return render(
        request,
        "hospitals/hospital_request_form.html",
        {
            "hospital": hospital,
            "errors": {},
            "form_data": {},
            "blood_types": blood_types,
        },
    )


# DONOR REGISTRATION
def donor_signup(request):
    """
    Donor sign up form.
    Creates a Donor record and logs the donor in if the data is valid.
    """
    if request.method == "POST":
        full_name = request.POST.get("fullName", "").strip()
        cpr = request.POST.get("cpr", "").strip()
        age_str = request.POST.get("age", "").strip()
        gender = request.POST.get("gender", "").strip()

        city = request.POST.get("city", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip().lower()

        blood_type = request.POST.get("blood_type", "").strip()
        last_donation_str = request.POST.get("last_donation_date", "").strip()
        health_notes = request.POST.get("health_notes", "").strip()

        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        contact_consent = bool(request.POST.get("contact_consent"))
        info_accuracy = bool(request.POST.get("info_accuracy_confirmed"))

        errors = {}
        form_data = request.POST.copy()

        # text fields
        if not full_name:
            errors["fullName"] = "Full name is required."
        if not email:
            errors["email"] = "Email is required."

        # age validation
        age = None
        if not age_str:
            errors["age"] = "Age is required."
        else:
            try:
                age = int(age_str)
                if age < 18 or age > 65:
                    errors["age"] = "Donors must be between 18 and 65."
            except ValueError:
                errors["age"] = "Please enter a valid age."

        # password checks
        if not password or password != confirm_password:
            errors["password"] = "Passwords must match and not be empty."

        # checkboxes
        if not contact_consent:
            errors["contact_consent"] = "Please allow hospitals to contact you."
        if not info_accuracy:
            errors["info_accuracy_confirmed"] = (
                "Please confirm the information is accurate."
            )

        # unique e-mail and CPR checks
        if email and Donor.objects.filter(email=email).exists():
            errors["email"] = "An account with this email already exists."
        if cpr and Donor.objects.filter(cpr=cpr).exists():
            errors["cpr"] = "This CPR / ID is already registered."

        # optional last donation date
        last_donation = None
        if last_donation_str:
            try:
                last_donation = datetime.strptime(
                    last_donation_str, "%Y-%m-%d"
                ).date()
            except ValueError:
                errors["last_donation_date"] = "Please use a valid date."

        if errors:
            return render(
                request,
                "donors/donor_signup.html",
                {"errors": errors, "form_data": form_data},
            )

        # create donor record
        donor = Donor.objects.create(
            full_name=full_name,
            cpr=cpr,
            age=age,
            gender=gender,
            city=city,
            phone=phone,
            email=email,
            blood_type=blood_type,
            last_donation_date=last_donation,
            health_notes=health_notes,
            password=password,  
            contact_consent=contact_consent,
            info_accuracy_confirmed=info_accuracy,
        )

        # auto-login after sign up
        request.session["donor_id"] = str(donor.pk)
        request.session["donor_name"] = donor.full_name

        return redirect("donor_signup_success")

    # GET – first load (empty form)
    return render(
        request,
        "donors/donor_signup.html",
        {"errors": {}, "form_data": {}},
    )


def donor_signup_success(request):
    """
    Simple success page after donor sign up.
    """
    return render(request, "donors/donor_signup_success.html")


# DONOR LOGIN / LOGOUT / DASHBOARD
def donor_login(request):
    """
    Simple donor login using email + plain-text password.
    Stores donor_id in the session after successful login.
    """

    
    if request.method == "GET" and request.session.get("donor_id"):
        return redirect("donor_dashboard")

    error = None
    form_data = {}

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()
        form_data["email"] = email

        donor = None
        try:
            donor = Donor.objects.get(email__iexact=email)
        except Donor.DoesNotExist:
            error = "Incorrect email or password."

        if donor and donor.password != password:
            error = "Incorrect email or password."

        if error:
            return render(
                request,
                "donors/donor_login.html",
                {"error": error, "form_data": form_data},
            )

        
        # SUCCESS LOGIN
        
        request.session["donor_id"] = str(donor.pk)
        request.session["donor_name"] = donor.full_name

       
        # REMEMBER ME FEATURE
       
        remember = request.POST.get("remember_me")
        print("REMEMBER VALUE:", remember)  

        if remember:
            # session lasts 7 days
           request.session.set_expiry(7 * 24 * 60 * 60)
        else:
            # session ends after 10 minutes
            request.session.set_expiry(10 * 60)

       
        print("SESSION EXPIRY (seconds):", request.session.get_expiry_age())

        return redirect("donor_dashboard")

    
    return render(
        request,
        "donors/donor_login.html",
        {"error": "", "form_data": {}},
    )


def donor_forgot_password(request):
    """
    Simple password reset for donors:
    - User enters email + new password + confirm password.
    - If email exists and passwords match, update donor.password.
    """

    error = None

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        new_password = request.POST.get("new_password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        # basic validations
        if not email or not new_password or not confirm_password:
            error = "Please fill in all fields."
        elif new_password != confirm_password:
            error = "Passwords do not match."
        else:
            try:
                donor = Donor.objects.get(email__iexact=email)
                donor.password = new_password
                donor.save()

                
                return redirect("donor_login")

            except Donor.DoesNotExist:
                error = "No donor found with this email."

    return render(
        request,
        "donors/donor_forgot_password.html",
        {"error": error}
    )

def donor_logout(request):
    """
    Clear only donor-related keys from the session.
    """
    request.session.pop("donor_id", None)
    request.session.pop("donor_name", None)
    return redirect("donor_login")


def donor_dashboard(request):
    """
    Donor dashboard.
    Shows blood requests that match the donor blood type.
    Also displays the donor's previous decisions (accept / reject)
    stored in the session.
    """
    donor_id = request.session.get("donor_id")

    if not donor_id:
        return redirect("donor_login")

    donor = get_object_or_404(Donor, pk=donor_id)

    try:
        all_requests_qs = BloodRequest.objects.all()
        all_requests = list(all_requests_qs)

        # read stored decisions from the session (accepted / rejected)
        responses = request.session.get("donor_request_responses", {})

        matching = []
        for req in all_requests:
            bt_req = (req.blood_type_needed or "").strip()
            bt_donor = (donor.blood_type or "").strip()

            if bt_req == bt_donor:
                # attach donor_status from session (accepted / rejected / None)
                req.donor_status = responses.get(str(req.id))
                matching.append(req)

        matching_sorted = sorted(matching, key=lambda r: r.created_at, reverse=True)

        matching_requests = matching_sorted[:5]
        matching_requests_count = len(matching)

    except DatabaseError as e:
        print("DEBUG donor_dashboard error:", e)
        matching_requests = []
        matching_requests_count = 0

    context = {
        "donor": donor,
        "total_donations": 0,
        "lives_supported": 0,
        "matching_requests_count": matching_requests_count,
        "matching_requests": matching_requests,
    }

    return render(request, "donors/donor_dashboard.html", context)


#  HOSPITAL REQUEST UPDATE / DELETE (PORTAL)
def hospital_request_update(request, request_id):
    """
    View and update an existing BloodRequest for the logged-in hospital.
    """
    hospital_id = request.session.get("hospital_id")
    if not hospital_id:
        return redirect("hospital_login")

    hospital = get_object_or_404(Hospital, pk=hospital_id)

    blood_request = get_object_or_404(BloodRequest, pk=request_id, hospital=hospital)

    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    urgency_choices = ["Critical", "High", "Medium", "Normal"]

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        blood_type = request.POST.get("blood_type", "").strip()
        units_str = request.POST.get("units", "").strip()
        urgency = request.POST.get("urgency", "Normal").strip()
        notes = request.POST.get("notes", "").strip()
        status_str = request.POST.get("status", "open").strip()  # open / closed

        errors = {}
        form_data = request.POST.copy()

        if not title:
            errors["title"] = "Request title is required."
        if not blood_type:
            errors["blood_type"] = "Blood type is required."

        
        units = None
        if units_str:
            try:
                units = int(units_str)
            except ValueError:
                errors["units"] = "Please enter a valid number of units."

        if errors:
            return render(
                request,
                "hospitals/hospital_request_update.html",
                {
                    "hospital": hospital,
                    "blood_request": blood_request,
                    "errors": errors,
                    "form_data": form_data,
                    "blood_types": blood_types,
                    "urgency_choices": urgency_choices,
                },
            )

        # save changes back to the database
        blood_request.title = title
        blood_request.blood_type_needed = blood_type
        blood_request.units = units or 1
        blood_request.urgency = urgency
        blood_request.notes = notes
        blood_request.is_active = (status_str == "open")
        blood_request.save()

        return redirect("hospital_dashboard")

    # pre-fill form with current values
    form_data = {
        "title": blood_request.title,
        "blood_type": blood_request.blood_type_needed,
        "units": blood_request.units,
        "urgency": blood_request.urgency,
        "notes": blood_request.notes,
        "status": "open" if blood_request.is_active else "closed",
    }

    return render(
        request,
        "hospitals/hospital_request_update.html",
        {
            "hospital": hospital,
            "blood_request": blood_request,
            "errors": {},
            "form_data": form_data,
            "blood_types": blood_types,
            "urgency_choices": urgency_choices,
        },
    )


def hospital_request_delete(request, request_id):
    """
    Delete a BloodRequest that belongs to the logged-in hospital.
    """
    hospital_id = request.session.get("hospital_id")
    if not hospital_id:
        return redirect("hospital_login")

    hospital = get_object_or_404(Hospital, pk=hospital_id)

    blood_request = get_object_or_404(BloodRequest, pk=request_id, hospital=hospital)

    if request.method == "POST":
        blood_request.delete()
        return redirect("hospital_dashboard")

    return render(
        request,
        "hospitals/hospital_request_delete.html",
        {
            "hospital": hospital,
            "blood_request": blood_request,
        },
    )


# SMALL HELPER + DONOR ACTIONS
def get_logged_in_donor(request):
    """
    Helper function.
    Returns the currently logged-in donor object or None.
    """
    donor_id = request.session.get("donor_id")
    if not donor_id:
        return None
    try:
        return Donor.objects.get(id=donor_id)
    except Donor.DoesNotExist:
        return None


def donor_request_decision(request, request_id):
    """
    Store the donor decision (accept / reject) for a specific BloodRequest
    both in the session and in MongoDB (DonorRequestResponse).
    """
    # donor must be logged in
    donor_id = request.session.get("donor_id")
    if not donor_id:
        return redirect("donor_login")

    # احضر كائن المتبرع من الـ DB
    donor = get_object_or_404(Donor, pk=donor_id)

    # make sure the BloodRequest exists (read-only check)
    blood_request = get_object_or_404(BloodRequest, pk=request_id)

    if request.method != "POST":
        return redirect("donor_dashboard")

    decision = request.POST.get("decision")
    if decision not in ["accepted", "rejected"]:
        messages.error(request, "Invalid action.")
        return redirect("donor_dashboard")

    
    try:
        client = MongoClient(settings.DATABASES["default"]["CLIENT"]["host"])
        db = client[settings.DATABASES["default"]["NAME"]]

        responses_coll = db["donor_request_responses"]

        responses_coll.insert_one(
            {
                "donor_id": int(donor.id),
                "donor_name": donor.full_name,
                "blood_request_id": int(blood_request.id),
                "status": decision,
                "decided_at": timezone.now().isoformat(),
            }
        )

    except Exception as e:
        
        print("MONGO INSERT ERROR:", repr(e))




    # ✅ 2) وبعدين خليه محفوظ بعد في الـ session (مثل قبل)
    responses = request.session.get("donor_request_responses", {})
    responses[str(blood_request.id)] = decision
    request.session["donor_request_responses"] = responses
    request.session.modified = True

    # show a short message to the user
    if decision == "accepted":
        messages.success(
            request,
            "Thank you! You have accepted this request. The hospital may contact you soon.",
        )
    else:
        messages.info(
            request,
            "You have declined this request. You can still donate to other requests.",
        )

    return redirect("donor_dashboard")



def donor_profile_edit(request):
    """
    Allow the logged-in donor to update their own profile
    (basic contact info, blood type, last donation date, and notes).
    """
    donor_id = request.session.get("donor_id")
    if not donor_id:
        return redirect("donor_login")

    donor = get_object_or_404(Donor, pk=donor_id)

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        city = request.POST.get("city", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip().lower()
        blood_type = request.POST.get("blood_type", "").strip()
        last_donation_str = request.POST.get("last_donation_date", "").strip()
        health_notes = request.POST.get("health_notes", "").strip()
        contact_consent = bool(request.POST.get("contact_consent"))

        errors = {}
        form_data = request.POST.copy()

        if not full_name:
            errors["full_name"] = "Full name is required."
        if not email:
            errors["email"] = "Email is required."

        # check email uniqueness (excluding this donor)
        if email and Donor.objects.filter(email=email).exclude(pk=donor.pk).exists():
            errors["email"] = "Another donor is already using this email."

        # optional last donation date
        last_donation = None
        if last_donation_str:
            try:
                last_donation = datetime.strptime(
                    last_donation_str, "%Y-%m-%d"
                ).date()
            except ValueError:
                errors["last_donation_date"] = "Please use a valid date (YYYY-MM-DD)."

        if errors:
            return render(
                request,
                "donors/donor_profile_edit.html",
                {
                    "donor": donor,
                    "errors": errors,
                    "form_data": form_data,
                },
            )

        # save changes to the donor record
        donor.full_name = full_name
        donor.city = city
        donor.phone = phone
        donor.email = email
        if blood_type:
            donor.blood_type = blood_type
        donor.last_donation_date = last_donation
        donor.health_notes = health_notes
        donor.contact_consent = contact_consent
        donor.save()

        # keep session name up to date
        request.session["donor_name"] = donor.full_name

        return redirect("donor_dashboard")

    # GET – pre-fill form with existing values
    form_data = {
        "full_name": donor.full_name,
        "city": donor.city,
        "phone": donor.phone,
        "email": donor.email,
        "blood_type": donor.blood_type,
        "last_donation_date": donor.last_donation_date.strftime("%Y-%m-%d")
        if donor.last_donation_date
        else "",
        "health_notes": donor.health_notes,
        "contact_consent": donor.contact_consent,
    }

    return render(
        request,
        "donors/donor_profile_edit.html",
        {
            "donor": donor,
            "errors": {},
            "form_data": form_data,
        },
    )
