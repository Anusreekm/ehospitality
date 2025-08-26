from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.utils.datetime_safe import date
from .models import PatientProfile, Appointment, MedicalHistory, Billing, HealthResource
from .forms import PatientRegisterForm, AppointmentForm, MedicalHistoryForm, BillingForm
from doctor.models import DoctorProfile
from datetime import datetime, timedelta
import stripe

User = get_user_model()

# Session-based login
def get_logged_in_user(request):
    if "user_id" in request.session:
        try:
            return User.objects.get(id=request.session["user_id"])
        except User.DoesNotExist:
            return None
    return None


def patient_register(request):
    if request.method == "POST":
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data["password"])
            user.role = "patient"
            user.save()
            PatientProfile.objects.create(user=user)
            return redirect("patient_login")
    else:
        form = PatientRegisterForm()
    return render(request, "patient/register.html", {"form": form})


def patient_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username, role="patient")
            if check_password(password, user.password):
                request.session["user_id"] = user.id
                request.session["role"] = "patient"
                return redirect("patient:patient_dashboard")
        except User.DoesNotExist:
            pass
        return render(request, "patient/login.html", {"error": "Invalid credentials"})
    return render(request, "patient/login.html")


def patient_dashboard(request):
    user = get_logged_in_user(request)
    if not user or user.role != "patient":
        return redirect("accounts:login")

    patient, created = PatientProfile.objects.get_or_create(user=user)

    appointments = Appointment.objects.filter(patient=patient)
    bills = Billing.objects.filter(patient=patient)
    prescriptions = patient.prescriptions.all().order_by("-created_at")

    return render(
        request,
        "patient/dashboard.html",
        {
            "patient": patient,
            "appointments": appointments,
            "bills": bills,
            "prescriptions": prescriptions,
        },
    )


def medical_history(request):
    user = get_logged_in_user(request)
    if not user or user.role != "patient":
        return redirect("patient_login")
    patient = PatientProfile.objects.get(user=user)
    history = MedicalHistory.objects.filter(patient=patient)
    return render(request, "patient/medical_history.html", {"history": history})


def add_medical_history(request):
    user = get_logged_in_user(request)
    if not user or user.role != "patient":
        return redirect("patient_login")
    patient = PatientProfile.objects.get(user=user)

    if request.method == "POST":
        form = MedicalHistoryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.patient = patient
            entry.save()
            return redirect("medical_history")
    else:
        form = MedicalHistoryForm()
    return render(request, "patient/add_medical_history.html", {"form": form})


def billing_list(request):
    user = get_logged_in_user(request)
    if not user or user.role != "patient":
        return redirect("patient_login")
    patient = PatientProfile.objects.get(user=user)
    bills = Billing.objects.filter(patient=patient)
    return render(request, "patient/billing_list.html", {"bills": bills})


def pay_bill(request, bill_id):
    user = get_logged_in_user(request)
    if not user or user.role != "patient":
        return redirect("patient_login")
    bill = get_object_or_404(Billing, id=bill_id)

    # Simple Stripe Checkout (placeholder)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"Bill {bill.id}"},
                "unit_amount": int(bill.amount * 100),
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="http://localhost:8000/patient/billing/",
        cancel_url="http://localhost:8000/patient/billing/",
    )
    return redirect(checkout_session.url, code=303)


def resources(request):
    resources = HealthResource.objects.all()
    return render(request, "patient/resources.html", {"resources": resources})


def generate_time_slots(start="09:00", end="17:00", interval=30):
    slots = []
    start_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    while start_time < end_time:  # exclude end time
        slots.append(start_time.strftime("%H:%M"))
        start_time += timedelta(minutes=interval)
    return slots


def book_appointment(request):
    user = get_logged_in_user(request)
    if not user or user.role != "patient":
        return redirect("patient_login")

    patient = PatientProfile.objects.get(user=user)
    doctors = DoctorProfile.objects.all()
    all_slots = generate_time_slots()
    available_slots = []

    selected_doctor = None
    selected_date = None
    error = None

    if request.method == "POST":
        doctor_id = request.POST.get("doctor")
        date_str = request.POST.get("date")
        time_val = request.POST.get("time")

        selected_doctor = get_object_or_404(DoctorProfile, id=doctor_id)
        selected_date = date_str

        if date_str:
            try:
                selected_date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                error = "Invalid date format."
            else:

                if selected_date_obj < date.today():
                    error = "You cannot book for past dates."
                else:

                    booked = Appointment.objects.filter(
                        doctor=selected_doctor,
                        date=selected_date_obj
                    ).values_list("time", flat=True)


                    booked_str = [t.strftime("%H:%M") for t in booked]
                    available_slots = [slot for slot in all_slots if slot not in booked_str]

                    if time_val:
                        if time_val not in available_slots:
                            error = "Slot not available!"
                        else:
                            try:
                                Appointment.objects.create(
                                    patient=patient,
                                    doctor=selected_doctor,
                                    date=selected_date_obj,
                                    time=datetime.strptime(time_val, "%H:%M").time()
                                )
                                return redirect("patient:patient_dashboard")
                            except IntegrityError:
                                error = "Sorry, this slot was just booked by another patient."

    return render(request, "patient/book_appointment.html", {
        "doctors": doctors,
        "time_slots": available_slots,
        "selected_doctor": selected_doctor.id if selected_doctor else None,
        "selected_date": selected_date,
        "today": date.today().strftime("%Y-%m-%d"),
        "error": error
    })



def edit_medical_history(request, history_id):
    user = get_logged_in_user(request)
    if not user or user.role != "patient":
        return redirect("patient_login")

    patient = PatientProfile.objects.get(user=user)
    entry = get_object_or_404(MedicalHistory, id=history_id, patient=patient)

    if request.method == "POST":
        form = MedicalHistoryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("medical_history")
    else:
        form = MedicalHistoryForm(instance=entry)

    return render(request, "patient/edit_medical_history.html", {"form": form, "entry": entry})

# Delete entry
def delete_medical_history(request, history_id):
    user = get_logged_in_user(request)
    if not user or user.role != "patient":
        return redirect("patient_login")

    patient = PatientProfile.objects.get(user=user)
    entry = get_object_or_404(MedicalHistory, id=history_id, patient=patient)
    entry.delete()
    return redirect("medical_history")

stripe.api_key = settings.STRIPE_SECRET_KEY

def pay_bill(request, bill_id):
    bill = get_object_or_404(Billing, id=bill_id)

    if request.method == "POST":
        # Create a Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "inr",
                    "product_data": {"name": f"Hospital Bill #{bill.id}"},
                    "unit_amount": int(bill.amount * 100)
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri(
                f"/patient/billing/success/{bill.id}/"
            ),
            cancel_url=request.build_absolute_uri(
                f"/patient/billing/cancel/{bill.id}/"
            ),

        )
        return redirect(checkout_session.url, code=303)

    return render(request, "patient/pay_bill.html", {"bill": bill})


def payment_success(request, bill_id):
    bill = get_object_or_404(Billing, id=bill_id)
    bill.status = "paid"   # ✅ mark as paid
    bill.save()
    return render(request, "patient/payment_success.html", {"bill": bill})


def payment_cancel(request, bill_id):
    bill = get_object_or_404(Billing, id=bill_id)
    return render(request, "patient/payment_cancel.html", {"bill": bill})

def resources(request):
    resources = HealthResource.objects.all().order_by("-published_at")
    return render(request, "patient/resources.html", {"resources": resources})
