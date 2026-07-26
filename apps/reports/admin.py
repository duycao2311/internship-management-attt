from django.contrib import admin
from .models import (
    InternshipAssignment, WeeklyReport, FinalReport, LecturerFeedback,
    DepartmentLecturerAssignment, InternshipTerm, MentorGroup,
    WeeklyDeadline, FinalDeadline, TermConfig,
    WeeklyReportGrade, FinalReportGrade,
)
import datetime


@admin.register(InternshipTerm)
class InternshipTermAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    readonly_fields = ('name',)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        today = datetime.date.today()
        if 'year' not in initial:
            initial['year'] = today.year
        if 'start_date' not in initial:
            initial['start_date'] = datetime.date(today.year, 6, 20)
        if 'end_date' not in initial:
            initial['end_date'] = datetime.date(today.year, 6, 20) + datetime.timedelta(weeks=10)
        return initial


@admin.register(InternshipAssignment)
class InternshipAssignmentAdmin(admin.ModelAdmin):
    list_display = ('application', 'lecturer', 'term', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'lecturer', 'term')
    search_fields = ('application__student__user__username', 'lecturer__user__username')


@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'week_number', 'is_submitted', 'is_locked', 'is_late', 'submitted_at')
    list_filter = ('is_submitted', 'is_locked', 'is_late', 'week_number')
    search_fields = ('assignment__application__student__user__username',)
    list_editable = ('is_locked',)


@admin.register(FinalReport)
class FinalReportAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'is_submitted', 'is_locked', 'is_late', 'submitted_at')
    list_filter = ('is_submitted', 'is_locked', 'is_late')
    search_fields = ('assignment__application__student__user__username',)
    list_editable = ('is_locked',)


@admin.register(LecturerFeedback)
class LecturerFeedbackAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at')


@admin.register(DepartmentLecturerAssignment)
class DepartmentLecturerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('department', 'lecturer', 'created_at')
    search_fields = ('department__organization_name', 'lecturer__user__username', 'lecturer__user__email')


@admin.register(MentorGroup)
class MentorGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'term', 'department', 'mentor', 'capacity', 'is_active')
    list_filter = ('term', 'department', 'is_active')


@admin.register(WeeklyDeadline)
class WeeklyDeadlineAdmin(admin.ModelAdmin):
    list_display = ('term', 'week_number', 'deadline', 'updated_by', 'updated_at')
    list_filter = ('term', 'week_number')
    list_editable = ('deadline',)


@admin.register(FinalDeadline)
class FinalDeadlineAdmin(admin.ModelAdmin):
    list_display = ('term', 'deadline', 'updated_by', 'updated_at')
    list_filter = ('term',)
    list_editable = ('deadline',)


@admin.register(TermConfig)
class TermConfigAdmin(admin.ModelAdmin):
    list_display = ('term', 'min_required_weeks')
    list_editable = ('min_required_weeks',)


@admin.register(WeeklyReportGrade)
class WeeklyReportGradeAdmin(admin.ModelAdmin):
    list_display = ('weekly_report', 'grader_type', 'score', 'graded_at')
    list_filter = ('grader_type',)


@admin.register(FinalReportGrade)
class FinalReportGradeAdmin(admin.ModelAdmin):
    list_display = ('final_report', 'grader_type', 'score', 'graded_at')
    list_filter = ('grader_type',)
