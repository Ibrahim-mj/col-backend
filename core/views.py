from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import ClassSerializer, AcademicSessionSerializer
from .models import Class, AcademicSession
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


class ListCreateAcademicSession(ListCreateAPIView):
    """To create or list academic sessions"""

    serializer_class = AcademicSessionSerializer
    queryset = AcademicSession.objects.all()

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            custom_resp = {
                "success": True,
                "message": "New Academic Session created successfully!",
                "data": response.data,
            }
            return Response(custom_resp, status=status.HTTP_201_CREATED)
        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            custom_resp = {
                "success": True,
                "message": "Academic Sessions Retrieved Successfully",
                "data": response.data,
            }
            return Response(custom_resp, status=status.HTTP_201_CREATED)
        return response


class RetrieveUpdateDestroyAcademicSession(RetrieveUpdateDestroyAPIView):

    serializer_class = AcademicSessionSerializer
    queryset = AcademicSession.objects.all()
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            custom_resp = {
                "success": True,
                "message": "Academic Session Retrieved Successfully",
                "data": response.data,
            }
            return Response(custom_resp, status=status.HTTP_200_OK)
        return response

    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            custom_resp = {
                "success": True,
                "message": "Academic Session Updated Successfully",
                "data": response.data,
            }
            return Response(custom_resp, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            custom_resp = {
                "success": True,
                "message": "Academic Session updated Successfully",
                "data": response.data,
            }
            return Response(custom_resp, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            custom_resp = {
                "success": True,
                "message": "Academic Session deleted Successfully",
                "data": response.data,
            }
            return Response(custom_resp, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)
