from django.contrib import admin
from .models import InternshipAssignment, WeeklyReport, FinalReport, LecturerFeedback, DepartmentLecturerAssignment, InternshipPeriod

@admin.register(InternshipPeriod)
class InternshipPeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)

@admin.register(InternshipAssignment)
class InternshipAssignmentAdmin(admin.ModelAdmin):
    list_display = ('application', 'lecturer', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'lecturer')
    search_fields = ('application__student__user__username', 'lecturer__user__username')

@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'assignment', 'week_number', 'status', 'created_at')
    list_filter = ('status', 'week_number')
    search_fields = ('title', 'assignment__application__student__user__username')

@admin.register(FinalReport)
class FinalReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'assignment', 'created_at')
    search_fields = ('title', 'assignment__application__student__user__username')

@admin.register(LecturerFeedback)
class LecturerFeedbackAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at')

@admin.register(DepartmentLecturerAssignment)
class DepartmentLecturerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('department', 'lecturer', 'created_at')
    search_fields = ('department__organization_name', 'lecturer__user__username', 'lecturer__user__email')
