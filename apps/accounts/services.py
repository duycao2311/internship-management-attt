import re
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def ensure_default_mentors(department_profile, count=6):
    """
    Ensure the department has at least 'count' mentors.
    If not, create the remaining mentors using a standard username format.
    """
    from .models import MentorProfile

    # Count existing mentors
    existing_count = MentorProfile.objects.filter(department=department_profile).count()
    if existing_count >= count:
        return

    mentors_to_create = count - existing_count

    # Generate a base slug for the username
    org_name = department_profile.organization_name
    if not org_name:
        org_name = department_profile.user.username

    # Convert to slug, e.g., "FPT Software" -> "fpt_software"
    base_slug = slugify(org_name).replace("-", "_")
    if not base_slug:
        base_slug = "company"

    created = 0
    index = 1

    while created < mentors_to_create:
        username = f"{base_slug}_mentor_{index}"
        
        # Check if username already exists
        if not User.objects.filter(username=username).exists():
            # Create user and profile
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    password='thuctapattt@',
                    role=User.MENTOR
                )
                
                # Signal `create_user_profile` will automatically create the `MentorProfile`
                # so we just need to fetch it and link it to the department
                mentor_profile = user.mentor_profile
                mentor_profile.department = department_profile
                mentor_profile.full_name = f"Mentor {index} - {org_name}"
                mentor_profile.save()
                
                created += 1
        
        index += 1
