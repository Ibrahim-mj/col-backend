from django.db import models

PaymentPurposeEnum = (
    ("REGISTRATION", "Registration"),
    ("COMMITMENT", "Commitment"),
    ("BOOKS", "Books"),
)


class BasePayment(models.Model):
    """
    Abstract base class for payments.
    """

    student = models.ForeignKey("users.User", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
    )  # Paystack transaction reference
    status = models.CharField(
        max_length=50, default="pending"
    )  # success/pending/failed
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.paid_by} - {self.amount} - {self.purpose}"


class RegistrationPayment(BasePayment):
    """
    Model representing a registration payment.
    """

    pass  # No additional fields for now


class Payment(BasePayment):
    """
    Model representing a payment.
    """

    academic_session = models.ForeignKey(
        "core.AcademicSession", on_delete=models.CASCADE
    )
    student_class = models.ForeignKey("core.Class", on_delete=models.CASCADE)
    purpose = models.CharField(choices=PaymentPurposeEnum, max_length=50)
    # purpose of payment (registration, commitment, etc.)

    def __str__(self):
        return f"{self.amount} for {self.purpose} on {self.paid_at}"


class FeeAmount(models.Model):
    """Model to manage the fee amounts for different levels and purpose based on Academic Session."""

    session = models.ForeignKey("core.AcademicSession", on_delete=models.CASCADE)
    student_class = models.ForeignKey("core.Class", on_delete=models.CASCADE)
    purpose = models.CharField(max_length=20, choices=PaymentPurposeEnum)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("session", "student_class", "purpose")  # prevent duplicates

    def __str__(self):
        return f"{self.session.name} | Level {self.level} | {self.get_type_display()}: ₦{self.amount}"