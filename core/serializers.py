from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import StudentProfile, TutorProfile
from .models import Class


class ClassSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    class_tutor = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.filter(is_staff=True)
    )
    class_level = serializers.IntegerField()
    student_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Class
        fields = "__all__"

    def validate_class_tutor(self, value):
        if not value.is_staff:
            raise ValidationError("The class tutor must be a staff member")
        return value

    def validate_student_ids(self, student_ids):
        if student_ids is not None:
            for student_id in student_ids:
                student = StudentProfile.objects.filter(user=student_id).first()
                if student is None:
                    raise ValidationError(
                        f"Student with ID {student_id} does not have a profile"
                    )
        return student_ids

    def validate(self, attrs):
        # I should validate if the class tutor being submitted has is_staff=True
        student_ids = attrs.get("student_ids", None)
        if student_ids is not None:
            attrs["students_ids"] = self.validate_student_ids(student_ids)
        return attrs

    def update(self, instance, validated_data):
        student_ids = validated_data.pop(
            "student_ids", None
        )  # for bulk assignment of students to class
        if student_ids is not None:
            for student_id in student_ids:
                # student = get_user_model().objects.filter(id=student_id).first()
                student = StudentProfile.objects.filter(user=student_id).first()
                student.student_class = instance
                student.save()
        instance.name = validated_data.get("name", instance.name)
        instance.class_tutor = validated_data.get("class_tutor", instance.class_tutor)
        instance.class_level = validated_data.get("class_level", instance.class_level)
        instance.save()
        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        class_students = StudentProfile.objects.filter(student_class=instance)
        print(class_students)
        rep["students"] = [
            {
                "id": student.user.id,  # the user_id
                "first_name": student.user.first_name,
                "last_name": student.user.last_name,
                "email": student.user.email,
            }
            for student in class_students
        ]
        return rep