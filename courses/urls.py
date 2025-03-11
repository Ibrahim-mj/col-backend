from django.urls import path

from . import views

urlpatterns = [
    path("courses/", views.CourseListCreateView.as_view(), name="courses-list-create"),
    path(
        "courses/<int:pk>/",
        views.CourseRetrieveUpdateDeleteView.as_view(),
        name="courses-retrieve-update-delete",
    ),
]
