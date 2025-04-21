from django.urls import path

from rest_framework.routers import DefaultRouter
from .views import PaymentView, RegistrationPaymentView, PaystackWebhookView

urlpatterns = [
    path("pay/", PaymentView.as_view(), name="payments"),
    path("registration-payment/", RegistrationPaymentView.as_view(), name="registration-payment"),
    path("webhook/paystack/", PaystackWebhookView.as_view(), name="paystack-webhook"),
]
