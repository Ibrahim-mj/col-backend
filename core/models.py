from django.db import models


class Class(models.Model):
    name = models.CharField(max_length=255)
    class_tutor = models.ForeignKey("users.User", on_delete=models.CASCADE)
    class_level = models.IntegerField()

    def __str__(self):
        return self.name
