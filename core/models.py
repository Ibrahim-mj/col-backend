from django.db import models


class AcademicSession(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ACADEMIC SESSION"

    def save(self, *args, **kwargs):
        if self.is_active:
            AcademicSession.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


class Class(models.Model):
    name = models.CharField(max_length=255)
    class_tutor = models.ForeignKey("users.User", on_delete=models.CASCADE)
    class_level = models.IntegerField()

    def __str__(self):
        return self.name
