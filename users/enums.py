from django.db import models

class UserTypes(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    TUTOR = "TUTOR", "Tutor"
    STUDENT = "STUDENT", "Student"


class AuthProviders(models.TextChoices):
    EMAIL = "EMAIL", "email"
    GOOGLE = "GOOGLE", "google"


class LevelChoices(models.TextChoices):
    LEVEL_100 = "100", "100"
    LEVEL_200 = "200", "200"
    LEVEL_300 = "300", "300"
    LEVEL_400 = "400", "400"
    LEVEL_500 = "500", "500"
    LEVEL_600 = "600", "600"
    LEVEL_700 = "700", "700"
