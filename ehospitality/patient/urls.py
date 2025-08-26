from django.urls import path
from . import views

app_name = "patient"

urlpatterns = [
    path("register/", views.patient_register, name="patient_register"),
    path("login/", views.patient_login, name="patient_login"),
    path("dashboard/", views.patient_dashboard, name="patient_dashboard"),

    #Appoinment
    path("appointment/book/", views.book_appointment, name="book_appointment"),

    # Billing
    path("billing/", views.billing_list, name="billing_list"),
    path("billing/pay/<int:bill_id>/", views.pay_bill, name="pay_bill"),
    path("billing/success/<int:bill_id>/", views.payment_success, name="payment_success"),
    path("billing/cancel/<int:bill_id>/", views.payment_cancel, name="payment_cancel"),

    # Resource
    path("resources/", views.resources, name="resources"),


]
