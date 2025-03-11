from rest_framework import serializers
from .models import Course
from core.models import AcademicSession, Class
from users.models import User


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "course_code",
            "course_title",
            "tutor",
            "class_name",
            "academic_session",
        ]

    def validate_course_code(self, value):
        """Validate the course code"""
        if not value.isalnum():
            raise serializers.ValidationError("Course code must be alphanumeric.")
        return value

    def validate(self, attrs):
        """Ensure the combination of course_code, class_name, and academic_session is unique."""
        course_code = attrs.get("course_code")
        class_name = attrs.get("class_name")
        academic_session = attrs.get("academic_session")

        if Course.objects.filter(
            course_code=course_code,
            class_name=class_name,
            academic_session=academic_session,
        ).exists():
            raise serializers.ValidationError(
                "A course with this code, class, and academic session already exists."
            )
        return attrs
