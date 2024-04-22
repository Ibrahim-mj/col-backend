from django.core.validators import EmailValidator, RegexValidator

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError

from .models import User, UserProfile




class UserSerializer(serializers.ModelSerializer):
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
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPES, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name"
            "user_type",
            "is_active",
            "is_staff",
        )

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.user_type = validated_data["user_type"]
        user.save()
        return user