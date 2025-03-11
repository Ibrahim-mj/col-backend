from rest_framework import serializers

from .models import Result
from users.models import User


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = [
            "student",
            "course",
            "score",
            "remark",
            "academic_session",
            "semester",
            "student_class",
            "date_created",
        ]

    def validate_student(self, value):
        """Ensure the associated user is of type student"""
        if not value.user_type == "student":
            raise serializers.ValidationError("User must be a student")
        if not value:
            raise serializers.ValidationError("Student field cannot be empty.")
        return value


class PartialResultSerializer(serializers.Serializer):
    """For validation of the results i bulk upload"""

    student = serializers.IntegerField()
    course = serializers.IntegerField()
    score = serializers.IntegerField()
    remark = serializers.CharField()

    def validate_student(self, value):
        """Ensure the associated user is of type student"""
        if not value.user_type == "student":
            raise serializers.ValidationError("User must be a student")
        if not value:
            raise serializers.ValidationError("Student field cannot be empty.")
        return value


class BulkResultUploadSerializer(serializers.Serializer):
    """For validation of the results i bulk upload"""

    academic_session = serializers.IntegerField()
    semester = serializers.IntegerField()
    student_class = serializers.IntegerField()
    results = serializers.ListField(child=PartialResultSerializer())


class BulkResultResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    successful_uploads = serializers.IntegerField()
    data = serializers.JSONField()  # Or a nested serializer for `data`
    errors = serializers.ListField(child=serializers.JSONField(), required=False)


class PartialResultViewSerializer(serializers.Serializer):
    """For viewing results with some fields (like displaying for a course)"""

    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        error_messages={"does_not_exist": "A student with this ID does not exist."},
    )
    score = serializers.IntegerField()
    remark = serializers.CharField()


class BulkResultViewResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField()  # Or a nested serializer for `data`


class StudentRankingSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        error_messages={"does_not_exist": "A student with this ID does not exist."},
    )
    total_score = serializers.DecimalField(max_digits=10, decimal_places=2)
    rank = serializers.IntegerField()
