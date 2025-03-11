from django.db.models import F, Sum, Window
from django.db.models.functions import Rank

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from drf_spectacular.utils import extend_schema

from .models import Result
from .serializers import (
    ResultSerializer,
    BulkResultUploadSerializer,
    BulkResultResponseSerializer,
    PartialResultViewSerializer,
    BulkResultViewResponseSerializer,
    StudentRankingSerializer,
)


class UploadStudentResult(generics.CreateAPIView):
    """To upload a student's result in a course"""

    serializer_class = ResultSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            custom_resp = {
                "success": True,
                "message": "Result uploaded successfully",
                "data": response.data,
            }
            return Response(custom_resp, status=status.HTTP_201_CREATED)
        return response


class BulkResultUpload(generics.CreateAPIView):
    """Handles bulk upload of students' results for a course"""

    serializer_class = BulkResultUploadSerializer
    # response_serializer_class = BulkResultResponseSerializer

    @extend_schema(
        request=BulkResultUploadSerializer, responses=BulkResultResponseSerializer
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        academic_session = data.get("academic_session", None)
        semester = data.get("semester", None)
        student_class = data.get("student_class")
        if not academic_session:
            custom_resp = {
                "success": False,
                "message": "Academic session not provided",
                "successful_uploads": 0,
            }

            return Response(custom_resp, status=status.HTTP_400_BAD_REQUEST)

        if not semester:
            custom_resp = {
                "success": False,
                "message": "Semester not provided",
                "successful_uploads": 0,
            }

            return Response(custom_resp, status=status.HTTP_400_BAD_REQUEST)

        if not student_class:
            custom_resp = {
                "success": False,
                "message": "Class not provided",
                "successful_uploads": 0,
            }

            return Response(custom_resp, status=status.HTTP_400_BAD_REQUEST)

        context = {
            "academic_session": academic_session,
            "semester": semester,
            "student_class": student_class,
        }

        results = data.get("results", [])
        if not results:
            custom_resp = {
                "success": False,
                "message": "Results not provided",
                "successful_uploads": 0,
            }

            return Response(custom_resp, status=status.HTTP_400_BAD_REQUEST)

        errors = []
        uploaded_results = []
        for result in results:
            student_result = {**context, **result}
            try:
                result_serializer = ResultSerializer(data=student_result)
                result_serializer.is_valid(raise_exception=True)
                self.perform_create(result_serializer)
                uploaded_results.append(result_serializer.data)
            except ValidationError as e:
                errors.append(
                    {
                        "student": result.get("student", "Not found"),
                        "result_data": result,
                        "errors": result_serializer.errors,
                    }
                )
        if errors:
            custom_resp = {
                "success": False,
                "message": "Results uploaded with some errors",
                "successful_uploads": len(uploaded_results),
                "data": {**context, "results": uploaded_results},
                "errors": errors,
            }
            return Response(custom_resp, status=status.HTTP_207_MULTI_STATUS)
        custom_resp = {
            "success": True,
            "message": "Results uploaded successfully",
            "successful_uploads": len(uploaded_results),
            "data": {**context, "results": uploaded_results},
        }
        headers = self.get_success_headers(result_serializer.data)
        return Response(custom_resp, status=status.HTTP_201_CREATED, headers=headers)


class CourseResultDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves, update or delete results for a particular course"""

    # serializer_class = BulkResultUploadSerializer

    @extend_schema(responses=BulkResultViewResponseSerializer)
    def get(self, request, *args, **kwargs):
        """Gets all the results for a class"""
        academic_session = kwargs.get("academic_session_id", None)
        student_class = kwargs.get("class_id", None)
        semester = kwargs.get("semester", None)
        course = kwargs.get("course_id", None)

        if not academic_session:
            custom_resp = {
                "success": False,
                "message": "Academic session not provided",
            }

            return Response(custom_resp, status=status.HTTP_400_BAD_REQUEST)

        if not semester:
            custom_resp = {
                "success": False,
                "message": "Semester not provided",
            }

            return Response(custom_resp, status=status.HTTP_400_BAD_REQUEST)

        if not student_class:
            custom_resp = {
                "success": False,
                "message": "Class not provided",
            }

        if not course:
            custom_resp = {
                "success": False,
                "message": "Course not provided",
            }

            return Response(custom_resp, status=status.HTTP_400_BAD_REQUEST)

        results = Result.objects.filter(
            academic_session=academic_session,
            semester=semester,
            student_class=student_class,
            course=course,
        )
        serializer = PartialResultViewSerializer(results, many=True)

        context = {
            "academic_session": academic_session,
            "student_class": student_class,
            "semester": semester,
            "course": course,
        }
        custom_resp = {
            "success": True,
            "message": "Results retrieved successfully",
            "data": {**context, "results": serializer.data},
        }
        return Response(custom_resp, status=status.HTTP_200_OK)


class ClassSemesterResultView(generics.RetrieveAPIView):

    def get(self, request, *args, **kwargs):
        """Gets a semester cumulative results for each student in a class"""
        academic_session = kwargs.get("academic_session_id", None)
        student_class = kwargs.get("class_id", None)
        semester = kwargs.get("semester", None)

        if not academic_session:
            custom_resp = {
                "success": False,
                "message": "Academic session not provided",
                "successful_uploads": 0,
            }

            return Response(custom_resp, status=status.HTTP_400_BAD_REQUEST)

        if not semester:
            custom_resp = {
                "success": False,
                "message": "Semester not provided",
                "successful_uploads": 0,
            }

            return Response(custom_resp, status=status.HTTP_400_BAD_REQUEST)

        if not student_class:
            custom_resp = {
                "success": False,
                "message": "Class not provided",
                "successful_uploads": 0,
            }

            return Response(custom_resp, status=status.HTTP_400_BAD_REQUEST)

        results = (
            Result.objects.filter(
                academic_session=academic_session,
                semester=semester,
                student_class=student_class,
            )
            .values("student")
            .annotate(
                total_score=Sum("score"),
                rank=Window(
                    expression=Rank(),
                    partition_by=[F("student_class")],
                    order_by=F("total_score").desc(),
                ),
            )
        )
        serializer = StudentRankingSerializer(results, many=True)

        context = {
            "academic_session": academic_session,
            "student_class": student_class,
            "semester": semester,
        }

        custom_resp = {
            "success": True,
            "message": "Class Results retrieved successfully",
            "data": {**context, "results": serializer.data},
        }
        return Response(custom_resp, status=status.HTTP_200_OK)
