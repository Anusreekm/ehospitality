from django import forms, template
from django.contrib.auth import get_user_model
from .models import Appointment, MedicalHistory, Billing
from doctor.models import DoctorAvailability
from datetime import datetime

User = get_user_model()


class PatientRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]



class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["doctor", "date", "time"]

    def clean(self):
        cleaned = super().clean()
        doctor = cleaned.get('doctor')
        date = cleaned.get('date')
        time = cleaned.get('time')
        if not (doctor and date and time):
            return cleaned

        weekday = date.weekday()
        avail_qs = DoctorAvailability.objects.filter(doctor=doctor, day_of_week=weekday,
                                                     start_time__lte=time, end_time__gte=time)
        if not avail_qs.exists():
            raise forms.ValidationError("Doctor is not available at the selected day/time.")

        if Appointment.objects.filter(doctor=doctor, date=date, time=time).exists():
            raise forms.ValidationError("This slot is already booked.")
        return cleaned


class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        fields = ["diagnosis", "medications", "allergies", "treatment"]


class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ["amount"]


register = template.Library()


@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})
