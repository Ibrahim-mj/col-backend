from core.utils import EmailThread

def send_announcement_email(title, message, recipients):
    subject = f"Announcement: {title}"
    body = message
    html_message=None
    recipient_list = [recipient.email for recipient in recipients]
    EmailThread(subject, body, html_message, recipient_list).start()