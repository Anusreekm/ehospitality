from django.contrib import admin
from .models import PatientProfile, Appointment, MedicalHistory, Billing, HealthResource


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "insurance_info")  # removed created_at


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "date", "time", "status")


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "diagnosis", "date")  # replaced condition & created_at with real fields


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "amount", "status", "created_at")


@admin.register(HealthResource)
class HealthResourceAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "published_at")  # removed link (not in model)
