from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from .models import User, StudentProfile, TutorProfile
from .enums import UserTypes, AuthProviders


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         if instance.user_type == UserTypes.STUDENT:
#             StudentProfile.objects.create(user=instance)
#         elif instance.user_type == UserTypes.TUTOR:
#             TutorProfile.objects.create(user=instance)


# @receiver(pre_save, sender=StudentProfile)
# def generate_student_id(sender, instance, **kwargs):
#     if not instance.student_id:
#         instance.student_id = f"COL/STU/{instance.matric_no}"
