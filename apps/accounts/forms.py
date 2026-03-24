from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, StudentProfile, DepartmentProfile, LecturerProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "role", "password1", "password2")


    class Meta:
        model = User
        fields = ("username", "password")

# --- Profile forms ---
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ["student_id", "class_name", "major", "phone"]

class DepartmentProfileForm(forms.ModelForm):
    class Meta:
        model = DepartmentProfile
        fields = ["organization_name", "contact_person", "email", "phone", "address", "description"]

class LecturerProfileForm(forms.ModelForm):
    class Meta:
        model = LecturerProfile
        fields = ["full_name", "faculty", "phone", "specialization"]
