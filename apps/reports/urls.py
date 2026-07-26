from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Student Routes
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/weekly/', views.weekly_report_list, name='weekly_report_list'),
    path('student/weekly/<int:week_number>/submit/', views.weekly_report_submit, name='weekly_report_submit'),
    path('student/final/', views.final_report_detail, name='final_report_detail'),

    # Student Moodle Dashboard
    path('student/moodle/', views.student_moodle_dashboard, name='student_moodle_dashboard'),
    path('student/moodle/week/<int:week_number>/', views.student_week_detail, name='student_week_detail'),

    # Old Mentor/Lecturer dashboards (kept for backward compat)
    path('mentor/', views.mentor_dashboard, name='mentor_dashboard'),
    path('lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('lecturer/student/<int:assignment_id>/', views.lecturer_student_detail, name='lecturer_student_detail'),
    path('lecturer/feedback/<str:report_type>/<int:report_id>/', views.lecturer_feedback_create, name='lecturer_feedback_create'),

    # Report detail + grading (shared mentor/lecturer)
    path('weekly/<int:report_id>/', views.weekly_report_detail, name='weekly_report_detail'),
    path('final/<int:report_id>/', views.final_report_grade_detail, name='final_report_grade_detail'),

    # Statistics
    path('statistics/', views.statistics_dashboard, name='statistics_dashboard'),
    path('statistics/export/', views.statistics_export, name='statistics_export'),
    path('statistics/export/excel/', views.statistics_export_excel, name='statistics_export_excel'),
    path('statistics/assignment/<int:assignment_id>/', views.statistics_assignment_detail, name='statistics_assignment_detail'),
    # Moodle-style dashboard
    path('dashboard/', views.moodle_dashboard, name='moodle_dashboard'),
    path('dashboard/week/<int:week_number>/', views.moodle_week_detail, name='moodle_week_detail'),
    path('dashboard/final/', views.moodle_final_detail, name='moodle_final_detail'),
    path('dashboard/grade/<str:report_type>/<int:report_id>/', views.quick_grade, name='quick_grade'),

    # Deadline editing (lecturer/admin)
    path('dashboard/deadline/weekly/<int:deadline_id>/edit/', views.edit_weekly_deadline, name='edit_weekly_deadline'),
    path('dashboard/deadline/final/<int:deadline_id>/edit/', views.edit_final_deadline, name='edit_final_deadline'),

    # Comments
    path('comment/<str:report_type>/<int:report_id>/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/reply/', views.reply_comment, name='reply_comment'),
]

