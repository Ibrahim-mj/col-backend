from django.urls import path

from . import views

urlpatterns = [
    path(
        "student/<str:student_id>/create/",
        views.UploadStudentResult.as_view(),
        name="upload-student-result",
    ),
    path("bulk-upload/", views.BulkResultUpload.as_view(), name="bulk-result-upload"),
    path(
        "class/<str:class_id>/session/<str:academic_session_id>/semester/<str:semester>/course/<str:course_id>",
        views.CourseResultDetailView.as_view(),
        name="course-result-detail",
    ),
    path(
        "class/<str:class_id>/session/<str:academic_session_id>/semester/<str:semester>/",
        views.ClassSemesterResultView.as_view(),
        name="course-result-detail",
    ),
]
