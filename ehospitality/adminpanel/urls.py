from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [

    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    # User management

    path("users/", views.manage_users, name="manage_users"),
    path("users/edit/<int:user_id>/", views.edit_user, name="edit_user"),
    path("users/delete/<int:user_id>/", views.delete_user, name="delete_user"),

    # Facility management
    path("facilities/", views.manage_facilities, name="manage_facilities"),
    path("facilities/add/", views.add_facility, name="add_facility"),
    path("facilities/edit/<int:facility_id>/", views.edit_facility, name="edit_facility"),
    path("facilities/delete/<int:facility_id>/", views.delete_facility, name="delete_facility"),

    # Appointment management
    path("appointments/", views.manage_appointments, name="manage_appointments"),
    path("appointments/delete/<int:appointment_id>/", views.delete_appointment, name="delete_appointment"),


    # Doctor Management
    path("manage-doctors/", views.manage_doctors, name="manage_doctors"),
    path("add-doctor/", views.add_doctor, name="add_doctor"),
    path("edit-doctor/<int:doctor_id>/", views.edit_doctor, name="edit_doctor"),
    path("delete-doctor/<int:doctor_id>/", views.delete_doctor, name="delete_doctor"),

    # Patient Management
    path("manage-patients/", views.manage_patients, name="manage_patients"),
    path("add-patient/", views.add_patient, name="add_patient"),
    path("edit-patient/<int:patient_id>/", views.edit_patient, name="edit_patient"),
    path("delete-patient/<int:patient_id>/", views.delete_patient, name="delete_patient"),

    # Resourse Management
    path("resources/", views.manage_resources, name="manage_resources"),
    path("resources/add/", views.add_resource, name="add_resource"),
    path("resources/edit/<int:pk>/", views.edit_resource, name="edit_resource"),
    path("resources/delete/<int:pk>/", views.delete_resource, name="delete_resource"),
]


