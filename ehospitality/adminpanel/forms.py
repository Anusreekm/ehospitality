from django import forms
from accounts.models import User
from patient.models import HealthResource,Appointment
from .models import Facility


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ["username","first_name","last_name", "email", "password", "role", "is_active"]

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = "__all__"

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "date", "time", "status"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }


class HealthResourceForm(forms.ModelForm):
    class Meta:
        model = HealthResource
        fields = ["title", "content"]




