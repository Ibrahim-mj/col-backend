from django.db import models


class Result(models.Model):
    """A student's result in a course for in a semester"""

    student = models.ForeignKey("users.User", on_delete=models.CASCADE)
    course = models.ForeignKey("courses.Course", on_delete=models.PROTECT)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )  # Score out of 100
    remark = models.CharField(
        max_length=50,
        choices=(("Passed", "Passed"), ("Failed", "Failed"), ("Nill", "Nill")),
        default="Nill",
    )
    academic_session = models.ForeignKey(
        "core.AcademicSession", on_delete=models.CASCADE
    )
    semester = models.IntegerField(
        choices=[(1, "First Semester"), (2, "Second Semester")]
    )
    student_class = models.ForeignKey("core.Class", on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course}'s {self.semester} semester result({self.score})"

    class Meta:
        unique_together = ("student", "semester", "course")

    def save(self, *args, **kwargs):
        # for the result remark
        if self.score >= 50:
            self.remark = "Passed"
        elif self.score <= 50:
            self.remark = "Failed"
        else:
            self.remark = "Nill"
        super().save(*args, **kwargs)


# Not needed; at least for now.

# class SemesterCumulativeResult(models.Model):
#     """Cumulative result of a student in a semester"""
#     student = models.ForeignKey("users.User", on_delete=models.CASCADE)
#     semester = models.IntegerField(choices=[(1, First Semester), (2, Second Semester)])
#     academic_session = models.ForeignKey("core.AcademicSession", on_delete=models.CASCADE)
#     total_score = models.IntegerField(default=0)
#     position = models.PositiveIntegerField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.student}'s cumulative result for {self.semester}"

#     class Meta:
#         unique_together = ("student", "semester", "session")

# class SessionCumulativeResult(models.Model):
#     """Cumulative result of a student in a semester"""
#     student = models.ForeignKey("users.User", on_delete=models.CASCADE)
#     academic_session = models.ForeignKey("core.AcademicSession", on_delete=models.CASCADE)
#     total_score = models.IntegerField(default=0)
#     position = models.PositiveIntegerField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.student}'s cumulative result for {self.session}"

#     class Meta:
#         unique_together = ("student", "session")
