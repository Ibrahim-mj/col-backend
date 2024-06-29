from django.urls import path
from . import views

urlpatterns = [
    path("classes/", views.ClassListCreateAPIView.as_view(), name="classes"),
    path(
        "classes/<int:pk>/",
        views.ClassRetrieveUpdateDestroyAPIView.as_view(),
        name="class-detail",
    ),
]
