from django.urls import path
from . import views
from . import views_profile

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/department/', views.department_dashboard, name='department_dashboard'),
    path('dashboard/lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/periods/', views.admin_period_manager, name='admin_period_manager'),
    path('dashboard/admin/periods/create/', views.admin_period_create, name='admin_period_create'),
    path('dashboard/admin/periods/<int:period_id>/edit/', views.admin_period_edit, name='admin_period_edit'),
    path('dashboard/admin/periods/<int:period_id>/delete/', views.admin_period_delete, name='admin_period_delete'),
    path('dashboard/admin/periods/<int:period_id>/toggle/', views.admin_period_toggle_active, name='admin_period_toggle_active'),
    path('dashboard/admin/assignments/', views.admin_assignment_manager, name='admin_assignment_manager'),
    path('dashboard/admin/assignments/<int:assignment_id>/edit/', views.admin_assignment_edit, name='admin_assignment_edit'),
    path('dashboard/admin/assignments/<int:assignment_id>/toggle/', views.admin_assignment_toggle_active, name='admin_assignment_toggle_active'),
    path('dashboard/admin/mappings/', views.admin_mapping_manager, name='admin_mapping_manager'),
    path('dashboard/admin/mappings/create/', views.admin_mapping_create, name='admin_mapping_create'),
    path('dashboard/admin/mappings/create/<int:department_id>/', views.admin_mapping_create, name='admin_mapping_create_with_dept'),
    path('dashboard/admin/mappings/<int:mapping_id>/edit/', views.admin_mapping_edit, name='admin_mapping_edit'),
    path('dashboard/admin/mappings/<int:mapping_id>/delete/', views.admin_mapping_delete, name='admin_mapping_delete'),
    path('dashboard/admin/external-requests/', views.admin_external_request_manager, name='admin_external_request_manager'),
    path('dashboard/admin/external-requests/<int:req_id>/approve/', views.admin_external_request_approve, name='admin_external_request_approve'),
    path('forbidden/', views.forbidden_view, name='forbidden'),

    # Profile routes
    path('profile/', views_profile.profile_redirect, name='profile'),
    path('profile/student/', views_profile.student_profile, name='student_profile'),
    path('profile/department/', views_profile.department_profile, name='department_profile'),
    path('profile/lecturer/', views_profile.lecturer_profile, name='lecturer_profile'),
]
