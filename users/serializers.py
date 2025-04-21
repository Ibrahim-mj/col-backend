from django.core.validators import EmailValidator, RegexValidator
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import User, StudentProfile, TutorProfile
from .utils import send_tutor_account_created_email, send_student_profile_creation_email
from .enums import UserTypes, AuthProviders


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
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with this email already exists.",
            ),
            EmailValidator(message="Invalid email address."),
        ],
        required=True,
        allow_blank=False,
    )
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
                r"^(\+234|0)(7[0-9]|8[0-9]|9[0-9])[0-9]{8}$",
                "Invalid phone number. Please enter a valid Nigerian phone number in one of the following formats: '08012345678', '0812-345-6789', '+234-812-345-6789', '2348123456789', '+234 812 345 6789', '0812 345 6789'.",
            ),
        ],
        required=False,
    )
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=UserTypes, default=UserTypes.STUDENT)
    

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
        read_only_fields = ("is_active", "is_staff", "user_type", "is_verified")

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.user_type = UserTypes.STUDENT
        user.save()
        return user

    def validate(self, data):
        # to make sure that the 'is_approved' field is only set to True by a staff
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
                r"^(\+234|0)(7[0-9]|8[0-9]|9[0-9])[0-9]{8}$",
                "Invalid phone number. Please enter a valid Nigerian phone number in one of the following formats: '08012345678', '0812-345-6789', '+234-812-345-6789', '2348123456789', '+234 812 345 6789', '0812 345 6789'.",
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
        user.user_type = UserTypes.TUTOR
        user.auth_provider = AuthProviders.EMAIL
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
        read_only_fields = ("student_id", "user")

        def validate_matric_no(self, value):
            if len(value) != 6:
                raise ValidationError("Matriculation number must be 6 characters long.")
            return value

        def create(self, validated_date):
            student = StudentProfile.objects.create(**validated_date)
            # Set the user field to the logged in user
            student.user = self.context["request"].user
            student.student_id = f"COL/STU/{student.matric_no}"
            student.save()
            send_student_profile_creation_email(student)
            return student

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['user'] = StudentUserSerializer(instance.user).data
    #     return data