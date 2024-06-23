from django.core.validators import EmailValidator, RegexValidator
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import User, StudentProfile, TutorProfile, AdminProfile
from .utils import send_tutor_account_created_email


class UserSerializer(
    serializers.ModelSerializer
):  # I am considering breaking this into two serializers for student and tutor. I do not have a good reason for this yet.
    """Just to deserialize the user model."""

    class Meta:
        model = User
        exclude = (
            "password",
            "auth_provider",
            "groups",
            "user_permissions",
            "last_login",
        )


class StudentUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        validators=[
            RegexValidator(
                r"^[a-zA-Z-' ]+$",
                "Name must include letters, hyphens, or apostrophes only",
            ),
        ],
        required=False,
    )

    last_name = serializers.CharField(
        validators=[
            RegexValidator(
                r"^[a-zA-Z-' ]+$",
                "Name must include letters, hyphens, or apostrophes only",
            ),
        ],
        required=False,
    )
    phone_number = serializers.CharField(
        validators=[
            RegexValidator(
                r"(^\+234\d{10}$)|(^(0[789]\d{9})$)x",
                "Phone number must be a valid Nigerian number in the format: '+234xxxxxxxxxx'.",
            ),
        ],
        required=False,
    )
    password = serializers.CharField(write_only=True)
    # user_type = serializers.ChoiceField(choices=User.USER_TYPES, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "user_type",
            "is_active",
            "is_verified",
            "is_approved",
        )
        read_only_fields = ("is_active", "is_staff", "user_type", "verified")

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.user_type = "student"
        user.save()
        return user

    def validate(self, data):
        # to make sure that the 'approved' field is only set to True by a staff
        if "is_approved" in data:
            request = self.context.get("request")
            if not request.user.is_staff:
                raise PermissionDenied("Only staff can approve students.")
        return data


class TutorUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        validators=[
            RegexValidator(
                r"^[a-zA-Z-' ]+$",
                "Name must include letters, hyphens, or apostrophes only",
            ),
        ],
        required=False,
    )

    last_name = serializers.CharField(
        validators=[
            RegexValidator(
                r"^[a-zA-Z-' ]+$",
                "Name must include letters, hyphens, or apostrophes only",
            ),
        ],
        required=False,
    )
    phone_number = serializers.CharField(
        validators=[
            RegexValidator(
                r"^\+234\d{10}$",
                "Phone number must be a valid Nigerian number in the format: '+234xxxxxxxxxx'.",
            ),
        ],
        required=False,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "user_type",
            "is_active",
            "is_staff",
            "is_admin",
        )
        read_only_fields = ("is_active", "is_staff", "user_type")

    def create(self, validated_data):
        validated_data["password"] = get_random_string(8)
        user = User.objects.create_user(**validated_data)
        user.user_type = "tutor"
        user.is_active = True
        user.is_staff = True
        user.verified = True
        user.is_approved = True
        user.save()
        send_tutor_account_created_email(user, validated_data)
        return user


class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ("email", "redirect_url")


class SetNewPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(
        min_length=8
    )  # TODO: Add validators to ensure strong password
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data


class TutorAdminProfile(serializers.ModelSerializer):
    class Meta:
        model = TutorProfile
        fields = ("user",)


# Seperating the serializers for tutor and student profiles due to need for different fields


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = (
            "user",
            "faculty",
            "department",
            "level",
            "hall_of_residence",
            "room_no",
            "matric_no",
            "student_id",
        )
        read_only_fields = ("student_id",)

        def validate_matric_no(self, value):
            if len(value) != 6:
                raise ValidationError("Matriculation number must be 6 characters long.")
            return value

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['user'] = StudentUserSerializer(instance.user).data
    #     return data
