from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
	STUDENT = 'student'
	DEPARTMENT = 'department'
	LECTURER = 'lecturer'
	ADMIN = 'admin'
	MENTOR = 'mentor'
	ROLE_CHOICES = [
		(STUDENT, 'Student'),
		(DEPARTMENT, 'Department'),
		(LECTURER, 'Lecturer'),
		(ADMIN, 'Admin'),
		(MENTOR, 'Mentor'),
	]
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)

	def __str__(self):
		return f"{self.username} ({self.get_role_display()})"

# --- Role-specific profiles ---
class StudentProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
	student_id = models.CharField(max_length=20)
	class_name = models.CharField(max_length=50)
	major = models.CharField(max_length=100)
	phone = models.CharField(max_length=20)

	def __str__(self):
		return f"StudentProfile: {self.user.username}"

class DepartmentProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='department_profile')
	organization_name = models.CharField(max_length=100)
	contact_person = models.CharField(max_length=100)
	email = models.EmailField()
	phone = models.CharField(max_length=20)
	address = models.CharField(max_length=200)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.organization_name or self.user.username

class LecturerProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lecturer_profile')
	full_name = models.CharField(max_length=100)
	faculty = models.CharField(max_length=100)
	phone = models.CharField(max_length=20)
	specialization = models.CharField(max_length=100)

	def __str__(self):
		return self.user.get_full_name() or self.full_name or self.user.username

class MentorProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
	department = models.ForeignKey(DepartmentProfile, on_delete=models.CASCADE, related_name='mentors', null=True, blank=True)
	full_name = models.CharField(max_length=100, blank=True)
	phone = models.CharField(max_length=20, blank=True)
	job_title = models.CharField(max_length=100, blank=True)

	def __str__(self):
		name = self.full_name or self.user.username
		org = self.department.organization_name if self.department else "No Dept"
		return f"{name} ({org})"
