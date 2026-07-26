from django.contrib import admin
from .models import User, StudentProfile, DepartmentProfile, LecturerProfile, MentorProfile

from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
	fieldsets = UserAdmin.fieldsets + (
		(None, {'fields': ('role',)}),
	)
	add_fieldsets = UserAdmin.add_fieldsets + (
		(None, {'fields': ('role',)}),
	)
	list_display = UserAdmin.list_display + ('role',)

admin.site.register(User, CustomUserAdmin)

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "student_id", "class_name", "major", "phone")

@admin.register(DepartmentProfile)
class DepartmentProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "organization_name", "contact_person", "email", "phone")

@admin.register(LecturerProfile)
class LecturerProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "full_name", "faculty", "phone", "specialization")

@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "department", "full_name", "phone", "job_title")
	list_filter = ("department",)