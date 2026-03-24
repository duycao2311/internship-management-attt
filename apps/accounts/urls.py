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
    path('forbidden/', views.forbidden_view, name='forbidden'),

    # Profile routes
    path('profile/', views_profile.profile_redirect, name='profile'),
    path('profile/student/', views_profile.student_profile, name='student_profile'),
    path('profile/department/', views_profile.department_profile, name='department_profile'),
    path('profile/lecturer/', views_profile.lecturer_profile, name='lecturer_profile'),
]
