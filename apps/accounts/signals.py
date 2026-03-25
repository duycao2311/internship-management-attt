from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import StudentProfile, DepartmentProfile, LecturerProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create the corresponding profile when a User is created or updated.
    Uses get_or_create to prevent duplication if the profile already exists.
    """
    if instance.role == User.STUDENT:
        StudentProfile.objects.get_or_create(user=instance)
    elif instance.role == User.DEPARTMENT:
        DepartmentProfile.objects.get_or_create(user=instance)
    elif instance.role == User.LECTURER:
        LecturerProfile.objects.get_or_create(user=instance)
