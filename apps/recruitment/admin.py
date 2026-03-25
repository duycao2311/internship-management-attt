from django.contrib import admin
from .models import InternshipPost, CV, Application

@admin.register(InternshipPost)
class InternshipPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'deadline')
    search_fields = ('title', 'department__organization_name')

@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'updated_at')
    search_fields = ('title', 'student__user__username', 'student__student_id', 'student__user__first_name', 'student__user__last_name')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'post', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('student__user__username', 'student__student_id', 'post__title', 'post__department__organization_name')
