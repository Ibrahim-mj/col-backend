from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from users.models import User

from .serializers import AnnouncementSerializer
from .models import Announcement
from .utils import send_announcement_email


class AnnouncementListCreateView(generics.ListCreateAPIView):
    serializer_class = AnnouncementSerializer
    queryset = Announcement.objects.all()

    def get(self, request, *args, **kwargs):
        data = super().get(request, *args, **kwargs)
        response = {
            "success": True,
            "message": "Announcements retrieved successfully",
            "data": data.data,
        }
        return Response(response, status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = serializer.data
        recipients = User.objects.filter(user_type=data['recipient'])
        send_announcement_email(data['title'], data['content'], recipients)
        headers = self.get_success_headers(serializer.data)
        response = {
            "success": True,
            "message": "Announcements created successfully",
            "data": data,
        }
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)