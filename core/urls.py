from django.urls import path
from . import views

urlpatterns = [
    path("classes/", views.ClassListCreateAPIView.as_view(), name="classes"),
    path(
        "classes/<int:pk>/",
        views.ClassRetrieveUpdateDestroyAPIView.as_view(),
        name="class-detail",
    ),
    path(
        "academic-sessions/",
        views.ListCreateAcademicSession.as_view(),
        name="list-create-academic-session",
    ),
    path(
        "academic-sessions/<int:pk>/",
        views.RetrieveUpdateDestroyAcademicSession.as_view(),
        name="retieve-update-destroy-academi-session",
    ),
]
