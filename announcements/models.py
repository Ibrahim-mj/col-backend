from django.db import models

class Announcement(models.Model):
    RECIPIENT_CHOICE = (
        ("tutor", "Tutor"),
        ("student", "Student"),
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    announcer = models.ForeignKey("users.User", on_delete=models.CASCADE)
    recipient = models.CharField(
        max_length=255, choices=RECIPIENT_CHOICE, blank=True, null=True
    )
    # attachments = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title