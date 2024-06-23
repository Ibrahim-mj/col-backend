import datetime

import jwt

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db import transaction
from django.conf import settings
from django.http import HttpRequest

from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_approved", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    USER_TYPES = (
        ("admin", "Admin"),
        ("tutor", "Tutor"),
        ("student", "Student"),
    )

    AUTH_PROVIDERS = {
        "email": "email",
        "google": "google",
    }

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    user_type = models.CharField(
        max_length=255, choices=USER_TYPES, blank=True, null=True
    )
    auth_provider = models.CharField(max_length=255, default=AUTH_PROVIDERS["email"])
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(
        default=True
    )  # we may use this to deactivate accounts of students who have graduated
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)  # This for email verification
    is_approved = models.BooleanField(default=False)  # This is for admin approval

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return (
            f"{self.first_name} {self.last_name}"
            if self.first_name or self.last_name
            else self.email
        )

    def generate_jwt_token(
        self,
    ):  # I may decide to accept the expiry time as a parameter
        """
        Generates a JSON Web Token that stores user's information
        """
        token = jwt.encode(
            {
                "id": self.pk,
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "user_type": self.user_type,
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(hours=1),  # Should I remove the expiry time?
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        return token

    def get_tokens_for_user(self):
        """
        Generates refresh and access tokens for user
        """
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


LEVEL_CHOICES = (
    ("100", "100"),
    ("200", "200"),
    ("300", "300"),
    ("400", "400"),
    ("500", "500"),
    ("600", "600"),
    ("700", "700"),
)


class UserProfile(models.Model):
    """
    Profile model for the three types of users fields specific to a user type
    are optional
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        abstract = True


class StudentProfile(UserProfile):
    student_id = models.CharField(max_length=255, blank=True, null=True)
    faculty = models.CharField(max_length=250, blank=True, null=True)
    department = models.CharField(max_length=250, blank=True, null=True)
    matric_no = models.CharField(max_length=20, blank=True, null=True)
    level = models.CharField(
        max_length=10, choices=LEVEL_CHOICES, blank=True, null=True
    )
    hall_of_residence = models.CharField(max_length=100, blank=True, null=True)
    room_no = models.CharField(max_length=10, blank=True, null=True)


class TutorProfile(UserProfile):
    pass


class AdminProfile(UserProfile):
    pass
