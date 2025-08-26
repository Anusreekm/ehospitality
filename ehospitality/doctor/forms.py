from django import forms
from .models import DoctorProfile, DoctorAvailability, Prescription, PrescriptionItem
from django.forms import inlineformset_factory
from accounts.models import User

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'department', 'bio']

class DoctorAvailabilityForm(forms.ModelForm):
    class Meta:
        model = DoctorAvailability
        fields = ['day_of_week', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

PrescriptionItemFormSet = inlineformset_factory(
    Prescription,
    PrescriptionItem,
    fields=("drug_name", "dosage", "frequency", "duration"),
    extra=3,
    can_delete=True,
    widgets={
        "drug_name": forms.TextInput(attrs={"class": "form-control"}),
        "dosage": forms.TextInput(attrs={"class": "form-control"}),
        "frequency": forms.TextInput(attrs={"class": "form-control"}),
        "duration": forms.TextInput(attrs={"class": "form-control"}),
    }
)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {field: forms.TextInput(attrs={"class": "form-control"}) for field in fields}

class DoctorForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['user', 'specialization', 'department']
        widgets = {field: forms.TextInput(attrs={"class": "form-control"}) for field in fields}