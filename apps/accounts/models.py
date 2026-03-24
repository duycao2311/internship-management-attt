from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
	STUDENT = 'student'
	DEPARTMENT = 'department'
	LECTURER = 'lecturer'
	ADMIN = 'admin'
	ROLE_CHOICES = [
		(STUDENT, 'Student'),
		(DEPARTMENT, 'Department'),
		(LECTURER, 'Lecturer'),
		(ADMIN, 'Admin'),
	]
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)

	def __str__(self):
		return f"{self.username} ({self.get_role_display()})"
