from django.urls import path
from . import views

app_name = 'recruitment'

urlpatterns = [
    # Department URLs
    path('department/posts/', views.post_list, name='department_post_list'),
    path('department/posts/create/', views.post_create, name='department_post_create'),
    path('department/posts/<int:pk>/edit/', views.post_update, name='department_post_update'),
    path('department/posts/<int:pk>/delete/', views.post_delete, name='department_post_delete'),
    path('department/applications/', views.department_application_list, name='department_application_list'),
    path('department/applications/<int:pk>/', views.department_application_detail, name='department_application_detail'),
    path('department/applications/<int:pk>/status/<str:status>/', views.department_application_status, name='department_application_status'),
    
    # Student URLs
    path('student/posts/', views.student_post_list, name='student_post_list'),
    path('student/posts/<int:pk>/', views.student_post_detail, name='student_post_detail'),
    path('student/posts/<int:pk>/apply/', views.student_apply, name='student_apply'),
    path('student/cv/', views.student_cv_list, name='student_cv_list'),
    path('student/applications/', views.student_application_list, name='student_application_list'),
    path('student/external-request/create/', views.student_external_request_create, name='student_external_request_create'),
    path('student/applications/<int:pk>/confirm/', views.student_confirm_placement, name='student_confirm_placement'),
]
