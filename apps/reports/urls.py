from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Student Routes
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/weekly/', views.weekly_report_list, name='weekly_report_list'),
    path('student/weekly/create/', views.weekly_report_create, name='weekly_report_create'),
    path('student/final/', views.final_report_detail, name='final_report_detail'),
    
    # Lecturer Routes
    path('lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('lecturer/student/<int:assignment_id>/', views.lecturer_student_detail, name='lecturer_student_detail'),
    path('lecturer/feedback/<str:report_type>/<int:report_id>/', views.lecturer_feedback_create, name='lecturer_feedback_create'),
]
