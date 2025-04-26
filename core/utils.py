import threading

from django.core.mail import send_mail

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings


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

# TODO: Reformat the errors to be consistent with the rest of the API

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
