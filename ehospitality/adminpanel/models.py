from django.db import models
class Facility(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    resources = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.department}"


