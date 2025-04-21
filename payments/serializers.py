from rest_framework import serializers

from .models import Payment, RegistrationPayment, FeeAmount
from users.models import User


class RegistrationPaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for the RegistrationPayment model.
    """

    class Meta:
        model = RegistrationPayment
        fields = [
            "id",
            "paid_by",
            "amount",
            "reference",
            "status",
            "paid_at",
        ]
        read_only_fields = ["id", "paid_by", "paid_at"]
        extra_kwargs = {
            "reference": {"required": False},
            "status": {"required": False},
            "paid_at": {"required": False},
            "message": {"required": False},
        }
        reference = serializers.CharField(
            max_length=100,
            required=False,
            read_only=True,
            default="",
            allow_blank=True,
        )
        status = serializers.CharField(
            max_length=50,
            required=False,
            read_only=True,
            default="pending",
        )
        paid_by = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(),
            required=False,
            write_only=True,
        )
        amount = serializers.DecimalField(
            max_digits=10,
            decimal_places=2,
            required=True,
        )

        def save(self, **kwargs):
            """
            Save the Payment instance.
            """
            student = kwargs.get("student")
            if not student:
                raise serializers.ValidationError("User must be provided.")
            self.validated_data["student"] = student
            return super().save(**kwargs)

class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Payment model.
    """

    class Meta:
        model = Payment

        reference = serializers.CharField(
            max_length=100,
            required=False,
            read_only=True,
            default="",
            allow_blank=True,
        )
        status = serializers.CharField(
            max_length=50,
            required=False,
            read_only=True,
            default="pending",
        )
        paid_by = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(),
            required=False,
            write_only=True,
        )
        amount = serializers.DecimalField(
            max_digits=10,
            decimal_places=2,
            required=True,
        )
        purpose = serializers.ChoiceField(
            choices=[
                ("REGISTRATION", "Registration"),
                ("COMMITMENT", "Commitment"),
                ("BOOKS", "Books"),
            ],
            required=True,
        )
        fields = [
            "id",
            "paid_by",
            "amount",
            "purpose",
            "reference",
            "status",
            "paid_at",
        ]
        read_only_fields = ["id", "paid_by", "paid_at"]
        extra_kwargs = {
            "reference": {"required": False},
            "status": {"required": False},
            "paid_at": {"required": False},
            "message": {"required": False},
        }

        def save(self, **kwargs):
            """
            Save the Payment instance.
            """
            student = kwargs.get("student")
            if not student:
                raise serializers.ValidationError("User must be provided.")
            self.validated_data["student"] = student
            return super().save(**kwargs)
