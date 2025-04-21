from urllib.parse import urlencode

import jwt

from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.urls import reverse
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.utils.crypto import get_random_string
from django.db import transaction

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.permissions import IsAdminUser, IsStaffUser, IsStaffOrOwner
from .models import User, StudentProfile
from .serializers import (
    UserSerializer,
    TutorUserSerializer,
    StudentProfileSerializer,
    StudentUserSerializer,
    ResendVerificationEmailSerializer,
    PasswordResetSerializer,
    SetNewPasswordSerializer,
)
from .utils import oauth, decode_token, send_verification, send_reset_password
from .enums import UserTypes, AuthProviders


# =============Student Registration========================

class StudentRegisterView(generics.CreateAPIView):
    """
    For students to register accounts through email and password.

    This view allows students to register their accounts by providing their email and password.
    Upon successful registration, a verification link will be sent to their email address for account verification.

    Methods:
        - post: Handles the HTTP POST request for student registration.

    Attributes:
        - serializer_class: The serializer class used for validating and deserializing the request data.

    Returns:
        - Response: A JSON response indicating the success of the registration and a message to check email for verification link.
    """

    serializer_class = StudentUserSerializer

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification(user, request)

        response = {
            "success": True,
            "message": "Your account has been created. Kindly check your email for verification link.",
        }
        return Response(response, status=status.HTTP_201_CREATED)


class AccountVerificationView(generics.RetrieveAPIView):
    """
    AccountVerificationView handles the verification of user accounts through a token-based mechanism.

    This view extends Django Rest Framework's RetrieveAPIView to provide a read-only endpoint.
    It is designed to decode a verification token sent to the user, verify its validity, and update the user's account status accordingly.

    Attributes:
        queryset: Specifies the queryset that this view will operate on. Here, it is set to all User objects.
        serializer_class: Points to the serializer class that should be used for serializing and deserializing data.

    Methods:
        get_object(self):
            Attempts to decode the provided token to find the corresponding user.
            - Returns: The User object if the token is valid and the user exists.
            - Raises: Http404 with an appropriate error message if the token is expired, invalid, or the user does not exist.

        retrieve(self, request, *args, **kwargs):
            Overrides the default retrieve method to verify the user's account upon successful verification.
            - Parameters:
                - request: The HttpRequest object.
                - *args: Variable length argument list.
                - **kwargs: Arbitrary keyword arguments.
            - Returns: HttpResponseRedirect to a URL with the verification status. The URL includes query parameters indicating the success or failure of the verification process, along with relevant user data and tokens if successful.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        """
        Decodes the token and gets the user object

        Returns:
            User: The User object if the token is valid and the user exists.

        Raises:
            Http404: If the token is expired, invalid, or the user does not exist.
        """

        token = self.kwargs.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["id"])
            return user
        except jwt.ExpiredSignatureError:
            raise Http404("Verification link has expired. Please request a new one.")
        except jwt.InvalidTokenError:
            raise Http404("Invalid token. Please request a new one.")
        except User.DoesNotExist:
            raise Http404("User does not exist.")

    @transaction.atomic()
    def retrieve(self, request, *args, **kwargs):
        """
        Activates the user account

        Parameters:
            request (HttpRequest): The HttpRequest object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponseRedirect: Redirects to a URL with the verification status. The URL includes query parameters indicating the success or failure of the verification process, along with relevant user data and tokens if successful.
        """

        redirect_url = settings.VERIFY_EMAIL_REDIRECT_URL
        # And I can actually use urlparse(redirect_url).netloc to if it is absolute;
        # If not, user request.build_absolute_url
        try:
            user = self.get_object()
            user.is_verified = True
            user.save()
            user_data = self.serializer_class(user).data
            url = f'{redirect_url}?{urlencode({"success": True, "message": "user verified successfully", "tokens": user.get_tokens_for_user()})}'
            return HttpResponseRedirect(url)
        except Exception as e:
            url = f"{redirect_url}?{urlencode({'success': False, 'message': 'An error occurred while verifying the user.', 'error': str(e) })}"
            return HttpResponseRedirect(url)


class ResendVerificationEmailView(generics.GenericAPIView):
    """
    Takes email address, redirect_url and resend verification email to user.

    This view is responsible for handling the resend verification email functionality.
    It takes the email address and redirect URL from the request data and attempts to resend the verification email to the user.
    If the user is already verified, it returns a response indicating that the user is already verified.
    If the user does not exist, it returns a response indicating that a user with that email does not exist.
    If an error occurs while sending the verification email, it returns a response with an error message.

    Methods:
    - post: Handles the POST request and performs the resend verification email logic.
    """

    serializer_class = ResendVerificationEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.filter(email=email).first()

            if not user:
                return Response(
                    {
                        "success": True,
                        "message": "You should receive a verification link if you provided a correct email.",
                    },
                    status=status.HTTP_200_OK,
                )

            if user.is_verified:
                return Response(
                    {
                        "success": False,
                        "message": "User is already verified.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            send_verification(user, request)
            return Response(
                {"success": True, "message": "You should receive a verification link if you provided a correct email."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"An error occurred while sending the verification email. {e}. Please try again later.",  # May ot be wise to include the exception here
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RequestPasswordResetView(generics.GenericAPIView):
    """
    Sends a password reset link to the provided email if user with that email exists.

    Methods:
    - post: Sends a password reset link to the provided email if user with that email exists.
    """

    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        """
        Sends a password reset link to the provided email if user with that email exists.

        Parameters:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - If the password reset link is sent successfully, returns a success response with a message.
        - If the user does not exist or is not active, returns an error response with a message.
        """
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            if user.auth_provider != AuthProviders.EMAIL:
                message = {
                    "success": False,
                    "message": "You did not sign up with email and password",
                }
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            elif user.is_verified:
                send_reset_password(user)
                message = {
                    "success": True,
                    "message": "You should receive a password reset link if you provided a correct email.",
                }
                return Response(message, status=status.HTTP_200_OK)

        else:
            message = {
                "success": True,
                "message": "You should receive a password reset link if you provided a correct email.",
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(generics.GenericAPIView):
    """
    Takes the token and a new password and resets the user's password

    Methods:
    - patch: Resets the user's password using the provided token and new password.
    """

    serializer_class = SetNewPasswordSerializer

    @transaction.atomic()
    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = request.data.get("token")
        password = serializer.validated_data["password"]
        try:
            payload = decode_token(token)
            user = User.objects.get(pk=payload["id"])
            user.set_password(password)
            user.save()
            response = {"success": True, "message": "Password reset successful."}
            return Response(response, status=status.HTTP_200_OK)
        except ValueError as e:
            response = {"success": False, "message": str(e)}
            return Response()


# ==============Student Login=============

class GoogleSignInView(APIView):
    """
    View for handling Google sign-in.

    This view redirects the user to the Google sign-in page for authentication.

    Methods:
        - get: Handles the GET request and redirects the user to the Google sign-in page.
    """

    def get(self, request):
        google = oauth.create_client("google")
        redirect_url = request.build_absolute_uri(
            reverse("users:google-signin-callback")
        )
        return google.authorize_redirect(request, redirect_url)


class GoogleSignInCallbackView(APIView):
    """
    View for handling the Google sign-in callback.

    This view is responsible for handling the callback from Google after a user has successfully signed in.
    It retrieves the user's profile information from Google and performs the necessary actions based on whether
    the user already exists or needs to be created.

    If the user already exists, the view generates a new access token and refresh token for the user.
    Else, it creates a new user account and redirects the user to the appropriate URL.

    Methods:
        - get: Handles the GET request for the Google sign-in callback.

    """

    def get(self, request):
        """
        Handles the GET request for the Google sign-in callback.

        This method retrieves the access token from the request, fetches the user's profile information from Google,
        and performs the necessary actions based on whether the user already exists or needs to be created.

        Returns:
            A response indicating the success or failure of the login or registration process.

        """
        token = oauth.google.authorize_access_token(request)
        resp = oauth.google.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", token=token
        )
        resp.raise_for_status()
        profile = resp.json()

        user = User.objects.filter(email=profile["email"]).first()
        if user is not None:
            if user.auth_provider != AuthProviders.GOOGLE:
                redirect_url = f"{settings.GOOGLE_SIGNIN_REDIRECT_URL}?{urlencode({{'success': False, 'message': 'You did not sign up with Google'}})}"
                return HttpResponseRedirect(redirect_url)
            # maybe restrict unapproved students here too.
            # tokens = user.get_tokens_for_user()
            # redirect_url = f"{settings.GOOGLE_SIGNIN_REDIRECT_URL}?{urlencode({'success': True, 'message': 'Login successful.', 'tokens': tokens})}"
            # return HttpResponseRedirect(redirect_url)
        else:
            password = get_random_string(10)
            # How do I get the user's phone number from google bai?? E still dey fail
            user = User.objects.create_user(
                profile["email"],
                password=password,
                auth_provider=AuthProviders.GOOGLE,
                user_type="student",
                first_name=profile["given_name"],
                last_name=profile["family_name"],
                is_verified=True,
            )
            user.save()
            redirect_url = f"{settings.GOOGLE_SIGNIN_REDIRECT_URL}?{
                urlencode(
                    { 
                    'success': True, 
                    'message': 'Registration Successful', 
                    'tokens': user.get_tokens_for_user() 
                }
                )
            }"
            return HttpResponseRedirect(redirect_url)

class StudentLoginView(TokenObtainPairView):
    """
    View to obtain both access and refresh tokens for a student.
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = User.objects.get(email=request.data["email"])
        if user.user_type != UserTypes.STUDENT:
            return Response(
                {"success": False, "message": "You need a student account to login here."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if user.is_verified == False:
            return Response(
                {"success": False, "message": "Please verify your email to login."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.is_active == False:
            return Response(
                {"success": False, "message": "Your account has been deactivated."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.paid_reg == False:
            return Response(
                {"success": False, "message": "You need to pay your registration fee to login."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # if user.is_approved == False:
        #     return Response(
        #         {"success": False, "message": "Your account is not approved yet."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        
        # maybe restrict unapproved students from loging in too.
        # user_type = user.user_type
        # response.data["user_type"] = user_type # Is this necessary?
        tokens = {
            "success": True,
            "message": "Token obtained successfully.",
            "tokens": response.data,
        }
        return Response(tokens, status=status.HTTP_200_OK)


# =============Tutor Registration========================
class TutorRegisterView(generics.CreateAPIView):
    """
    For the admin tutor to create accounts for a tutor.

    This view allows the admin tutor to create accounts for tutors. It is restricted to admin users only.
    The tutor receives an email notification containing sign in instructions.

    Attributes:
        serializer_class (Serializer): The serializer class used for validating and deserializing the request data.

    Methods:
        post(request, *args, **kwargs): Handles the HTTP POST request and creates a tutor account.

    """

    serializer_class = TutorUserSerializer
    permission_classes = [IsAdminUser]

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "success": True,
            "message": "Tutor account created successfully. Ask the tutor to check their email for further instructions.",
        }
        return Response(response, status=status.HTTP_201_CREATED)


# =============Tutor Login========================

class TutorLoginView(TokenObtainPairView):
    """
    View to obtain both access and refresh tokens for a student.
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = User.objects.get(email=request.data["email"])
        if user.user_type != UserTypes.TUTOR:
            return Response(
                {"success": False, "message": "You need a student account to login here."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # if user.is_approved == False:
        #     return Response(
        #         {"success": False, "message": "Your account is not approved yet."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        
        # maybe restrict unapproved students from loging in too.
        # user_type = user.user_type
        # response.data["user_type"] = user_type # Is this necessary?
        tokens = {
            "success": True,
            "message": "Token obtained successfully.",
            "tokens": response.data,
        }
        return Response(tokens, status=status.HTTP_200_OK)



class UserListView(generics.ListAPIView):
    """
    A view that lists all users: students, admin, or tutors.
    Attributes:
        queryset (QuerySet): The queryset of User objects.
        serializer_class (Serializer): The serializer class for User objects.

    Methods:
        get_queryset(): Returns the filtered queryset based on the provided filters.
        get(request, *args, **kwargs): Retrieves a list of users based on the provided filters.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        user_type = self.request.query_params.get("user_type", None)
        is_approved = self.request.query_params.get("is_approved", None)
        if user_type is not None:
            queryset = User.objects.filter(is_verified=True).filter(user_type=user_type)
        if is_approved is not None:
            queryset = queryset = User.objects.filter(is_verified=True).filter(
                is_approved=is_approved
            )
        else:
            queryset = User.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        """
        Retrieve a list of users based on the provided filters.

        Users can be filtered by user_type or is_approved.
        Only users whose emails are verified are included in the list.


        Example:
        To retrieve a list of all students:
        GET /all-users/?user_type=student

        To retrieve a list of all verified students:
        GET /all-users/?user_type=student&is_approved=true

        Returns:
            A response containing the list of users and a success message.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = {
            "success:": True,
            "message": "Users retrieved successfully.",
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)


class StudentUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user instance.

    This view allows administrators, tutors, or the owner of the user instance to perform
    retrieval, update, and deletion operations on a user.

    Methods:
    - get: Retrieves a user instance.
    - put: Updates a user instance.
    - patch: Partially updates a user instance.
    - delete: Deletes a user instance.
    """

    queryset = User.objects.all()
    serializer_class = StudentUserSerializer
    permission_classes = [IsStaffOrOwner]

    def get_object(self):
        user_id = self.kwargs.get("pk")
        user = get_object_or_404(User, id=user_id)
        return user

    def get(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except:
            return Response(
                {"success": False, "message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(user)
        response = {
            "success": True,
            "message": "User retrieved successfully.",
            "data": serializer.data,  # TODO manage user data sent to the client
        }
        return Response(response, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except:
            return Response(
                {"success": False, "message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "success": True,
            "message": "User updated successfully.",
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except:
            return Response(
                {"success": False, "message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "success": True,
            "message": "User updated successfully.",
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except:
            return Response(
                {"success": False, "message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.delete()
        response = {"success": True, "message": "User deleted successfully."}
        return Response(response, status=status.HTTP_204_NO_CONTENT)


class TutorUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    This view allows administrators, tutors, or the owner of a student instance to retrieve, update, or delete the student's information.

    Methods:
    - get: Retrieves the student instance.
    - put: Updates the student instance.
    - patch: Partially updates the student instance.
    - delete: Deletes the student instance.
    """

    queryset = User.objects.all()
    serializer_class = TutorUserSerializer
    permission_classes = [IsAdminUser]

    def get_object(self):
        user_id = self.kwargs.get("pk")
        user = get_object_or_404(User, id=user_id)
        return user

    def get(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except:
            return Response(
                {"success": False, "message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(user)
        response = {
            "success": True,
            "message": "User retrieved successfully.",
            "data": serializer.data,  # TODO manage user data sent to the client
        }
        return Response(response, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except:
            return Response(
                {"success": False, "message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "success": True,
            "message": "User updated successfully.",
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except:
            return Response(
                {"success": False, "message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "success": True,
            "message": "User updated successfully.",
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except:
            return Response(
                {"success": False, "message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.delete()
        response = {"success": True, "message": "User deleted successfully."}
        return Response(response, status=status.HTTP_204_NO_CONTENT)

class StudentProfileView(generics.ListCreateAPIView):
    """
    View for creating and listing student profiles.

    This view allows administrators, tutors, or the owner of a student instance to create and list student profiles.

    Methods:
    - get: Retrieves a list of student profiles.
    - post: Creates a new student profile.

    """

    serializer_class = StudentProfileSerializer
    queryset = StudentProfile.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieves a list of student profiles.

        Returns:
            A response containing the list of student profiles and a success message.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = {
            "success": True,
            "message": "Student profiles retrieved successfully.",
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Creates a new student profile.

        Returns:
            A response indicating the success of the profile creation and a message.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "success": True,
            "message": "Student profile created successfully.",
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_201_CREATED)


class StudentUserProfile(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete view for the student's profile
    Can only be accessed by the staff or the owner
    """

    serializer_class = StudentProfileSerializer
    # queryset =     UserProfile.objects.filter(user__user_type="student")
    queryset = StudentProfile.objects.all()
    permission_classes = [IsStaffOrOwner]

    def get_object(self):
        user_id = self.kwargs.get("pk")
        print(f'user: {user_id}')
        # student_profile = get_object_or_404(StudentProfile, user=user_id)
        student_profile = StudentProfile.objects.get(user=user_id)
        print(f'student_profile: {student_profile}')
        return student_profile

    def retrieve(self, request, *args, **kwargs):
        try:
            student_profile = self.get_object()
        except:
            # print(student_profile)
            return Response(
                {"success": False, "message": "User profile not found not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(student_profile)
        response = {
            "success": True,
            "message": "User profile retrieved successfully.",
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)


# class PairTokenObtainView(TokenObtainPairView):
#     """
#     View to obtain both access and refresh tokens for a user.
#     """

#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         user = User.objects.get(email=request.data["email"])
#         if user.is_verified == False:
#             return Response(
#                 {"success": False, "message": "Please verify your email to login."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         # maybe restrict unapproved students from loging in too.
#         # user_type = user.user_type
#         # response.data["user_type"] = user_type # Is this necessary?
#         tokens = {
#             "success": True,
#             "message": "Token obtained successfully.",
#             "tokens": response.data,
#         }
#         return Response(tokens, status=status.HTTP_200_OK)

# ============For All Users===================

class RefreshTokenView(TokenRefreshView):
    """
    A view for refreshing authentication tokens.

    This view extends the `TokenRefreshView` class provided by the Django Rest Framework SimpleJWT library.
    It handles the POST request to refresh an existing authentication token and returns a new token.

    Methods:
    - post: Handles the POST request to refresh the token and returns the new token.

    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        tokens = {
            "success": True,
            "message": "Token obtained successfully.",
            "tokens": response.data,
        }
        return Response(tokens, status=status.HTTP_200_OK)
