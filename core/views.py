from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import ClassSerializer
from .models import Class
from .permissions import IsStaffUser


class ClassListCreateAPIView(ListCreateAPIView):
    serializer_class = ClassSerializer
    queryset = Class.objects.all()
    # permission_classes = [IsAuthenticated, IsStaffUser]

    def post(self, request, *args, **kwargs):
        data = super().post(request, *args, **kwargs)
        response = {
            "success": True,
            "message": "Class created successfully",
            "data": data.data,
        }
        return Response(response, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        data = super().get(request, *args, **kwargs)
        response = {
            "success": True,
            "message": "Classes retrieved successfully",
            "data": data.data,
        }
        return Response(response, status=status.HTTP_200_OK)


class ClassRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ClassSerializer
    queryset = Class.objects.all()
    # permission_classes = [IsAuthenticated, IsStaffUser]

    def get(self, request, *args, **kwargs):
        """
        Returns a single class instance including its students.
        """
        data = super().get(request, *args, **kwargs)
        response = {
            "success": True,
            "message": "Class retrieved successfully",
            "data": data.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """ """
        data = super().put(request, *args, **kwargs)
        response = {
            "success": True,
            "message": "Class updated successfully",
            "data": data.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        This endpoint partially updates a class. It only updates the fields that are provided in the request data.
        for convenience, it accept a list of student_ids and assigns all of them to the class.

        Example:
        {
            "name": "level 1",
            "student_ids": [1, 2, 3]
        }
        """
        data = super().patch(request, *args, **kwargs)
        response = {
            "success": True,
            "message": "Class updated successfully",
            "data": data.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            response = {
                "success": True,
                "message": "Class deleted successfully",
            }
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        return Response(response, status=status.HTTP_204_NO_CONTENT)
