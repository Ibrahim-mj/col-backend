import threading

import jwt

from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

oauth = OAuth()

google_config = settings.AUTHLIB_OAUTH_CLIENTS["google"]
oauth.register(
    name="google",
    client_id=google_config["client_id"],
    client_secret=google_config["client_secret"],
    authorize_url=google_config["authorize_url"],
    authorize_params=google_config["authorize_params"],
    access_token_url=google_config["access_token_url"],
    access_token_params=google_config["access_token_params"],
    client_kwargs=google_config["client_kwargs"],
    jwks_uri=google_config["jwks_uri"],
)


def format_drf_errors(errors):
    formatted_errors = []

    for field, messages in errors.items():
        error_type = "non_field_error" if field == "non_field_errors" else "field_error"
        if isinstance(messages, list):
            for message in messages:
                formatted_errors.append(
                    {"field": field, "message": str(message), "type": error_type}
                )
        else:
            formatted_errors.append(
                {"field": field, "message": str(messages), "type": error_type}
            )

    return formatted_errors


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and isinstance(response.data, dict):
        formatted_errors = format_drf_errors(response.data)
        response.data = {
            "success": False,
            "message": "Validation error occurred",
            "errors": formatted_errors,
        }

    return response


def decode_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    return payload


class EmailThread(threading.Thread):
    def __init__(self, subject: str, message: str, html_message: str, recipients: list):
        self.subject = subject
        self.message = message
        self.html_message = html_message
        self.recipients = recipients
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            subject=self.subject,
            message=self.message,
            from_email=f"Circle of Learning MSSNUI <{settings.DEFAULT_FROM_EMAIL}>",
            html_message=self.html_message,
            recipient_list=self.recipients,
            fail_silently=False,
        )


def send_verification_email(verification_link, user) -> None:
    subject = "Circle of Learning, MSSNUI  - Verify your email"
    message = f"Assalaamu 'alaykum {user.first_name},\n\nPlease verify your email by clicking on the link below:\n\n{verification_link}\n\n This link will expire in 24 hours.\n\nIf you did not register for an account, please ignore this email.\n\nBest regards,\COL MSSNUI"
    html_message = f"<p>Assalaamu 'alaykum {user.first_name},</p><p>Your Account is successfully created. Please verify your email by clicking on the link below:</p><p><a href='{verification_link}'>Verify Email</a></p><p>This link will expire in 24 hours.</p><p>If you did not register for an account, please ignore this email.</p><p>Best regards,<br>COL MSSNUI</p>"
    recipients = [user.email]
    EmailThread(subject, message, html_message, recipients).start()


def send_verification(user, request) -> None:  # TODO: add error logging
    token = user.generate_jwt_token()
    verification_link = request.build_absolute_uri(
        reverse("users:verify-email", kwargs={"token": token})
    )
    send_verification_email(verification_link, user)


def send_reset_password_email(password_reset_link, user) -> None:
    subject = "Circle of Learning, MSSNUI - Reset your password"
    message = f"Assalaamu 'alaykum, {user.first_name},\n\nYou requested a password reset. Please reset your password by clicking on the link below:\n\n{password_reset_link}\n\n This link will expire in 24 hours.\n\nIf you did not request a password reset, please ignore this email.\n\nBest regards,\nEcoVanguard Club"
    html_message = f"<p>Assalaamu 'alaykum, {user.first_name},</p><p>You requested a password reset. Please reset your password by clicking on the link below:</p><p><a href='{password_reset_link}'>Reset Password</a></p><p>This link will expire in 24 hours.</p><p>If you did not request a password reset, please ignore this email.</p><p>Best regards,<br>EcoVanguard Club</p>"
    recipients = [user.email]
    EmailThread(subject, message, html_message, recipients).start()


def send_reset_password(user) -> None:
    token = user.generate_jwt_token()
    password_reset_link = f"{settings.RESET_PASSWORD_REDIRECT_URL}?token={token}"
    send_reset_password_email(password_reset_link, user)


def send_tutor_account_created_email(user, validated_data):
    html_message = f"""
            <p>Dear Ustaadh {user.first_name},</p>

            <p>Assalaamu 'alaykum</p>

            <p>Your tutor account has been created successfully.</p>

            <p>Your login credentials are:</p>
            <ul>
                <li>Email: {user.email}</li>
                <li>Password: {validated_data['password']}</li>
            </ul>

            <p>Regards,</p>
            <p>Admin</p>
            """
    send_mail(
        subject="Circle of Learning, MSSNUI - Tutor Account Created",
        message=(
            f"Dear Ustaadh {user.first_name},\n\n"
            "Assalaamu 'alaykum \n\n"
            "Your tutor account has been created successfully.\n\n"
            "Your login credentials are:\n"
            f"Email: {user.email}\n"
            f"Password: {validated_data['password']}\n\n"
            "Regards,\n"
            "Admin"
        ),
        from_email="Circle of Learning MSSNUI",
        recipient_list=[user.email],
        fail_silently=False,
        html_message=html_message,
    )

def send_student_profile_creation_email(student_profile):
    # How write a function to send an email to the student with his profile detaails when his profile is created?
    html_message = f"""
            <p>Dear {student_profile.user.first_name},</p>

            <p>Assalaamu 'alaykum</p>

            <p>Your student profile has been created successfully.</p>

            <p>Your student ID is: {student_profile.student_id}</p>

            <p>Regards,</p>
            <p>Admin</p>
            """
    send_mail(
        subject="Circle of Learning, MSSNUI - Student Profile Created",
        message=(
            f"Dear {student_profile.user.first_name},\n\n"
            "Assalaamu 'alaykum \n\n"
            "Your student profile has been created successfully.\n\n"
            f"Your student ID is: {student_profile.student_id}\n\n"
            "Regards,\n"
            "Admin"
        ),
        from_email="Circle of Learning MSSNUI",
        recipient_list=[student_profile.user.email],
        fail_silently=False,
        html_message=html_message,
    )