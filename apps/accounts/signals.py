from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import StudentProfile, DepartmentProfile, LecturerProfile, MentorProfile
from .services import ensure_default_mentors

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
    elif instance.role == User.MENTOR:
        MentorProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=DepartmentProfile)
def create_default_mentors_for_department(sender, instance, created, **kwargs):
    """
    Trigger the auto-creation of 6 default mentors when a new DepartmentProfile is saved.
    Using transaction.on_commit to ensure it runs after the current database transaction is fully committed.
    """
    transaction.on_commit(lambda: ensure_default_mentors(instance))
