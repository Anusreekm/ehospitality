from django.db import models
from django.conf import settings

# --- Doctor profile ---
class DoctorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=120, blank=True)
    department = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.specialization or 'Doctor'})"


# 0 = Monday ... 6 = Sunday
DAYS = [(i, ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][i]) for i in range(7)]

class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('doctor', 'day_of_week', 'start_time', 'end_time')
        ordering = ('doctor', 'day_of_week', 'start_time')

    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


# --- E-prescription ---
class Prescription(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey('patient.PatientProfile', on_delete=models.CASCADE, related_name='prescriptions')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rx #{self.pk} - {self.patient.user.username} by {self.doctor.user.username}"

class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    drug_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=120, help_text="e.g., 500 mg")
    frequency = models.CharField(max_length=120, help_text="e.g., 1-0-1")
    duration = models.CharField(max_length=120, help_text="e.g., 5 days")

    def __str__(self):
        return f"{self.drug_name} ({self.dosage})"
