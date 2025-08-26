from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from accounts.utils import get_session_user, require_role
from accounts.models import User
from .models import DoctorProfile, DoctorAvailability, Prescription
from .forms import DoctorProfileForm, DoctorAvailabilityForm, PrescriptionForm, PrescriptionItemFormSet
from patient.models import PatientProfile, Appointment, MedicalHistory
from patient.models import Billing


def _get_doctor(request):
    user = require_role(request, ['doctor'])
    if not user:
        messages.error(request, "Please login as a doctor.")
        return None, redirect('accounts:login')
    try:
        doc = user.doctor_profile
    except DoctorProfile.DoesNotExist:
        doc = DoctorProfile.objects.create(user=user)
    return doc, None

# ------------ dashboard ------------
def dashboard(request):
    doc, bad = _get_doctor(request)
    if bad: return bad
    appts = Appointment.objects.filter(doctor=doc).order_by('date', 'time')[:10]
    return render(request, 'doctor/dashboard.html', {'doctor': doc, 'appointments': appts})

# ------------ appointments ------------
def appointments_list(request):
    doc, bad = _get_doctor(request)
    if bad: return bad
    status = request.GET.get('status')
    qs = Appointment.objects.filter(doctor=doc).order_by('-date', '-time')
    if status:
        qs = qs.filter(status=status)
    return render(request, 'doctor/appointments_list.html', {'appointments': qs})

def appointment_confirm(request, pk):
    doc, bad = _get_doctor(request)
    if bad: return bad
    appt = get_object_or_404(Appointment, pk=pk, doctor=doc)
    appt.status = 'confirmed'
    appt.save()
    messages.success(request, 'Appointment confirmed.')
    return redirect('doctor:appointments_list')

def appointment_cancel(request, pk):
    doc, bad = _get_doctor(request)
    if bad: return bad
    appt = get_object_or_404(Appointment, pk=pk, doctor=doc)
    appt.status = 'cancelled'
    appt.save()
    messages.info(request, 'Appointment cancelled.')
    return redirect('doctor:appointments_list')

def appointment_complete(request, pk):
    doc, bad = _get_doctor(request)
    if bad: return bad
    appt = get_object_or_404(Appointment, pk=pk, doctor=doc)
    appt.status = 'completed'
    appt.save()
    messages.success(request, 'Appointment marked completed.')
    return redirect('doctor:appointments_list')

# ------------ patient details ------------
def patient_detail(request, patient_id):
    doc, bad = _get_doctor(request)
    if bad: return bad
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    appts = Appointment.objects.filter(doctor=doc, patient=patient).order_by('-date', '-time')
    histories = MedicalHistory.objects.filter(patient=patient).order_by('-date')
    rx = patient.prescriptions.order_by('-created_at')[:10]
    return render(request, 'doctor/patient_detail.html', {
        'doctor': doc, 'patient': patient, 'appointments': appts, 'histories': histories, 'prescriptions': rx
    })

# ------------ availability ------------
def availability_list(request):
    doc, bad = _get_doctor(request)
    if bad: return bad
    avails = DoctorAvailability.objects.filter(doctor=doc).order_by('day_of_week', 'start_time')
    return render(request, 'doctor/availability_list.html', {'doctor': doc, 'availabilities': avails})

def availability_create(request):
    doc, bad = _get_doctor(request)
    if bad: return bad
    if request.method == 'POST':
        form = DoctorAvailabilityForm(request.POST)
        if form.is_valid():
            avail = form.save(commit=False)
            avail.doctor = doc
            # basic validation: start < end
            if avail.start_time >= avail.end_time:
                messages.error(request, 'Start time must be before end time.')
            else:
                # prevent overlaps on same day for this doctor
                overlaps = DoctorAvailability.objects.filter(
                    doctor=doc, day_of_week=avail.day_of_week,
                    start_time__lt=avail.end_time, end_time__gt=avail.start_time
                ).exists()
                if overlaps:
                    messages.error(request, 'This interval overlaps an existing availability.')
                else:
                    avail.save()
                    messages.success(request, 'Availability saved.')
                    return redirect('doctor:availability_list')
    else:
        form = DoctorAvailabilityForm()
    return render(request, 'doctor/availability_form.html', {'form': form})

def availability_delete(request, pk):
    doc, bad = _get_doctor(request)
    if bad: return bad
    a = get_object_or_404(DoctorAvailability, pk=pk, doctor=doc)
    a.delete()
    messages.info(request, 'Availability removed.')
    return redirect('doctor:availability_list')

def availability_feed(request):

    doc, bad = _get_doctor(request)
    if bad: return bad
    data = [{
        'dow': a.day_of_week,
        'start': str(a.start_time),
        'end': str(a.end_time),
    } for a in DoctorAvailability.objects.filter(doctor=doc)]
    return JsonResponse({'availability': data})

# ------------ e-prescribing ------------
def prescribe(request, patient_id):
    doc, bad = _get_doctor(request)
    if bad: return bad
    patient = get_object_or_404(PatientProfile, pk=patient_id)

    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            rx = form.save(commit=False)
            rx.doctor = doc
            rx.patient = patient
            rx.save()
            formset.instance = rx
            formset.save()
            messages.success(request, 'Prescription saved.')
            return redirect('doctor:patient_detail', patient_id=patient.id)
    else:
        form = PrescriptionForm()
        formset = PrescriptionItemFormSet()
    return render(request, 'doctor/prescribe_form.html', {'form': form, 'formset': formset, 'patient': patient})


def add_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = appointment.doctor
            prescription.patient = appointment.patient
            prescription.save()

            items = formset.save(commit=False)
            for item in items:
                item.prescription = prescription
                item.save()

            # 🔹 Create Billing entry linked to prescription
            Billing.objects.create(
                patient=appointment.patient,
                amount=500.00,  # example consultation fee
                status="unpaid"
            )

            messages.success(request, "Prescription saved and bill generated.")
            return redirect("doctor:dashboard")
    else:
        form = PrescriptionForm()
        formset = PrescriptionItemFormSet()

    return render(request, "doctor/add_prescription.html", {
        "appointment": appointment,
        "form": form,
        "formset": formset,
    })