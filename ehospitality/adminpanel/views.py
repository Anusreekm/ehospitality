from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from doctor.models import DoctorProfile
from patient.models import PatientProfile, HealthResource,Appointment
from .forms import UserForm, FacilityForm, AppointmentForm,HealthResourceForm
from accounts.models import User
from .models import Facility
from django.contrib import messages


def manage_appointments(request):
    appointments = Appointment.objects.all().order_by("-date", "-time")
    return render(request, "adminpanel/manage_appointments.html", {"appointments": appointments})

# Edit appointment

def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect("adminpanel:manage_appointments")
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, "adminpanel/edit_appointment.html", {"form": form})

# Delete appointment
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Appointment deleted successfully ❌")
        return redirect("adminpanel:manage_appointments")
    return render(request, "adminpanel/delete_appointment.html", {"appointment": appointment})
def admin_dashboard(request):
    # counts
    user_count = User.objects.count()
    doctor_count = DoctorProfile.objects.count()
    patient_count = PatientProfile.objects.count()
    facility_count = Facility.objects.count()
    resource_count = HealthResource.objects.count()
    appointment_count = Appointment.objects.count()

    appointments = Appointment.objects.all().order_by("-date")

    return render(request, "adminpanel/dashboard.html", {
        "user_count": user_count,
        "doctor_count": doctor_count,
        "patient_count": patient_count,
        "facility_count": facility_count,
        "resource_count": resource_count,
        "appointment_count": appointment_count,

        "appointments": appointments,
    })


# ------------------ USER MANAGEMENT ------------------
def manage_users(request):
    users = User.objects.all()
    return render(request, "adminpanel/manage_users.html", {"users": users})


def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("adminpanel:manage_users")
    else:
        form = UserForm(instance=user)
    return render(request, "adminpanel/user_form.html", {"form": form, "type": "Edit"})


def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect("adminpanel:manage_users")


# ------------------ FACILITY MANAGEMENT ------------------
def manage_facilities(request):
    facilities = Facility.objects.all()
    return render(request, "adminpanel/facilities.html", {"facilities": facilities})


def add_facility(request):
    if request.method == "POST":
        form = FacilityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("adminpanel:manage_facilities")
    else:
        form = FacilityForm()
    return render(request, "adminpanel/add_facility.html", {"form": form, "type": "Add"})


def edit_facility(request, facility_id):
    facility = get_object_or_404(Facility, id=facility_id)
    if request.method == "POST":
        form = FacilityForm(request.POST, instance=facility)
        if form.is_valid():
            form.save()
            return redirect("adminpanel:manage_facilities")
    else:
        form = FacilityForm(instance=facility)
    return render(request, "adminpanel/add_facility.html", {"form": form, "type": "Edit"})


def delete_facility(request, facility_id):
    facility = get_object_or_404(Facility, id=facility_id)
    facility.delete()
    return redirect("adminpanel:manage_facilities")


# ------------------ APPOINTMENT MANAGEMENT ------------------
def manage_appointments(request):
    appointments = Appointment.objects.select_related("patient", "doctor").order_by("-date")
    return render(request, "adminpanel/manage_appointments.html", {"appointments": appointments})


def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.delete()
    return redirect("adminpanel:manage_appointments")

# ---------------- Doctor Management ----------------

def manage_doctors(request):
    doctors = DoctorProfile.objects.all()
    return render(request, "adminpanel/manage_doctors.html", {"doctors": doctors})


def add_doctor(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "doctor"
            user.save()
            DoctorProfile.objects.create(user=user)
            return redirect("adminpanel:manage_doctors")
    else:
        form = UserForm()
    return render(request, "adminpanel/user_form.html", {"form": form, "type": "Add Doctor"})


def edit_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    form = UserForm(request.POST or None, instance=doctor.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("adminpanel:manage_doctors")
    return render(request, "adminpanel/user_form.html", {"form": form, "type": "Edit Doctor"})


def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    doctor.user.delete()  # deletes both doctor profile and user
    return redirect("adminpanel:manage_doctors")


# ---------------- Patient Management ----------------

def manage_patients(request):
    patients = PatientProfile.objects.select_related("user").all()
    return render(request, "adminpanel/manage_patients.html", {"patients": patients})

def add_patient(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "patient"
            user.save()
            PatientProfile.objects.get_or_create(user=user)  # prevent duplicates
            return redirect("adminpanel:manage_patients")
    else:
        form = UserForm()
    return render(request, "adminpanel/user_form.html", {"form": form, "type": "Add Patient"})

def edit_patient(request, patient_id):
    patient = get_object_or_404(PatientProfile, id=patient_id)
    form = UserForm(request.POST or None, instance=patient.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("adminpanel:manage_patients")
    return render(request, "adminpanel/user_form.html", {"form": form, "type": "Edit Patient"})


def delete_patient(request, patient_id):
    patient = get_object_or_404(PatientProfile, id=patient_id)
    patient.user.delete()  # deletes both patient profile and user
    return redirect("adminpanel:manage_patients")




# List resources
def manage_resources(request):
    resources = HealthResource.objects.all().order_by("-published_at")
    return render(request, "adminpanel/manage_resources.html", {"resources": resources})

# Add new resource
def add_resource(request):
    if request.method == "POST":
        form = HealthResourceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Health resource added successfully.")
            return redirect("adminpanel:manage_resources")
    else:
        form = HealthResourceForm()
    return render(request, "adminpanel/add_resource.html", {"form": form})

# Edit resource
def edit_resource(request, pk):
    resource = get_object_or_404(HealthResource, pk=pk)
    if request.method == "POST":
        form = HealthResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, "Health resource updated successfully.")
            return redirect("adminpanel:manage_resources")
    else:
        form = HealthResourceForm(instance=resource)
    return render(request, "adminpanel/edit_resource.html", {"form": form, "resource": resource})

# Delete resource
def delete_resource(request, pk):
    resource = get_object_or_404(HealthResource, pk=pk)
    if request.method == "POST":
        resource.delete()
        messages.success(request, "Health resource deleted successfully.")
        return redirect("adminpanel:manage_resources")
    return render(request, "adminpanel/delete_resource.html", {"resource": resource})