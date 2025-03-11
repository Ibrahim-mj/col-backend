from django.db import models


class Course(models.Model):

    course_code = models.CharField(max_length=10)
    course_title = models.CharField(max_length=250)
    tutor = models.ForeignKey("users.User", on_delete=models.PROTECT)
    class_name = models.ForeignKey("core.Class", on_delete=models.CASCADE)
    academic_session = models.ForeignKey(
        "core.AcademicSession", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.course_title

    class Meta:
        unique_together = ("course_code", "class_name", "academic_session")
