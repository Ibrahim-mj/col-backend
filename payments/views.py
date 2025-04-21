import hashlib
import hmac
from django.conf import settings
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError


from .utils import init_payment
from .models import Payment, RegistrationPayment, FeeAmount
from .serializers import PaymentSerializer, RegistrationPaymentSerializer

class RegistrationPaymentView(APIView):
    """
    View to handle registration payments.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = RegistrationPaymentSerializer

    def post(self, request, *args, **kwargs):
        """
        Initialize a registration payment.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        with transaction.atomic():
            payment = serializer.save(student=user)  # saves the basic payment data

            response_data = init_payment(
                user.email, serializer.validated_data["amount"], for_reg=True
            )

            if response_data["status"]:
                payment.reference = response_data["data"]["reference"]
                payment.save()

                return Response(
                    {
                        "success": True,
                        "message": "Payment initialized successfully.",
                        "data": {
                            "authorization_url": response_data["data"][
                                "authorization_url"
                            ],
                            "access_code": response_data["data"]["access_code"],
                            "reference": response_data["data"]["reference"],
                            "payment_id": serializer.data["id"],
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                raise ValidationError(
                    {
                        "success": False,
                        "message": response_data["message"],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

class PaymentView(APIView):
    """
    View to handle payments(handles only reg payment for now).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def post(self, request, *args, **kwargs):
        """
        Initialize a payment.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        with transaction.atomic():
            payment = serializer.save(student=user)  # saves the basic payment data

            response_data = init_payment(
                user.email, serializer.validated_data["amount"]
            )

            if response_data["status"]:
                payment.reference = response_data["data"]["reference"]
                payment.save()

                return Response(
                    {
                        "success": True,
                        "message": "Payment initialized successfully.",
                        "data": {
                            "authorization_url": response_data["data"][
                                "authorization_url"
                            ],
                            "access_code": response_data["data"]["access_code"],
                            "reference": response_data["data"]["reference"],
                            "payment_id": serializer.data["id"],
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                raise ValidationError(
                    {
                        "success": False,
                        "message": response_data["message"],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )


class PaystackWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        raw_body = request.body

        # To compute the HMAC hash
        computed_hash = hmac.new(
            key=bytes(settings.PAYSTACK_SECRET_KEY, "utf-8"),
            msg=raw_body,
            digestmod=hashlib.sha512,
        ).hexdigest()

        # To get the signature from the request header
        signature = request.META.get("HTTP_X_PAYSTACK_SIGNATURE")

        # To verify the signature
        if not hmac.compare_digest(computed_hash, signature):
            return Response(
                {"success": False, "message": "Invalid signature"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            data = request.data
            event = data.get("event")
            data = data.get("data")

            if event == "charge.success":
                if data["metadata"]["purpose"] == "registration":
                    # Handle registration payment success
                    payment = RegistrationPayment.objects.filter(reference=data["reference"]).first()

                    if payment:
                        if payment.amount > data["amount"] / 100:
                            payment.status = "not complete"
                        payment.status = "success"
                        student = payment.paid_by
                        student.paid_reg = True
                        student.save()
                        payment.save()
                        return Response(
                            {"success": True, "message": "Payment successful"},
                            status=status.HTTP_200_OK,
                        )
                else:
                    payment = Payment.objects.filter(reference=data["reference"]).first()

                    if payment:
                        if payment.amount > data["amount"] / 100:
                            payment.status = "not complete"
                        payment.status = "success"
                        payment.save()
                        return Response(
                            {"success": True, "message": "Payment successful"},
                            status=status.HTTP_200_OK,
                        )

            else:
                raise ValidationError(
                    {
                        "success": False,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )