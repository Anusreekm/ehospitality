from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class PatientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    insurance_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    doctor = models.ForeignKey("doctor.DoctorProfile", on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    class Meta:
        unique_together = ('doctor', 'date', 'time')
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.date} {self.time} - Dr.{self.doctor.user.username} with {self.patient.user.username}"


class MedicalHistory(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    medications = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"History for {self.patient.user.username} on {self.date}"


class HealthResource(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
class Billing(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="bills")
    prescription = models.OneToOneField(
        "doctor.Prescription", on_delete=models.SET_NULL, null=True, blank=True, related_name="bill"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[("unpaid", "Unpaid"), ("paid", "Paid")], default="unpaid")
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill {self.id} - {self.patient.user.username} ({self.status})"


class HealthResource(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_patient_profile(sender, instance, created, **kwargs):
    if created and hasattr(instance, "role") and instance.role == "patient":
        PatientProfile.objects.get_or_create(user=instance)