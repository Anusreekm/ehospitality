from django.urls import path
from . import views

app_name = 'doctor'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # appointments
    path('appointments/', views.appointments_list, name='appointments_list'),
    path('appointments/<int:pk>/confirm/', views.appointment_confirm, name='appointment_confirm'),
    path('appointments/<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('appointments/<int:pk>/complete/', views.appointment_complete, name='appointment_complete'),

    # patient detail
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),

    # availability
    path('availability/', views.availability_list, name='availability_list'),
    path('availability/new/', views.availability_create, name='availability_create'),
    path('availability/<int:pk>/delete/', views.availability_delete, name='availability_delete'),
    path('availability/feed/', views.availability_feed, name='availability_feed'),  # JSON for calendars

    # e-prescribing
    path('prescribe/<int:patient_id>/', views.prescribe, name='prescribe'),

    path("prescription/add/<int:appointment_id>/", views.add_prescription, name="add_prescription"),

]
