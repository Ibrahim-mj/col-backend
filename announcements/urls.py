from django.urls import path

from . import views

urlpatterns = [
    path("", views.AnnouncementListCreateView.as_view(), name="announcement-list-create")
]