from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard')
	if request.method == 'POST':
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			user = form.get_user()
			login(request, user)
			return redirect('dashboard')
		else:
			messages.error(request, 'Invalid username or password')
	else:
		form = AuthenticationForm()
	return render(request, 'accounts/login.html', {'form': form})


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import User

def role_required(role):
	def decorator(view_func):
		@login_required
		def _wrapped_view(request, *args, **kwargs):
			if hasattr(request.user, 'role') and request.user.role == role:
				return view_func(request, *args, **kwargs)
			return redirect('forbidden')
		return _wrapped_view
	return decorator

@login_required
def dashboard_redirect(request):
	if request.user.role == User.STUDENT:
		return redirect('student_dashboard')
	elif request.user.role == User.DEPARTMENT:
		return redirect('department_dashboard')
	elif request.user.role == User.LECTURER:
		return redirect('lecturer_dashboard')
	elif request.user.role == User.ADMIN:
		return redirect('admin_dashboard')
	else:
		return redirect('forbidden')

@role_required(User.STUDENT)
def student_dashboard(request):
	return render(request, 'accounts/student_dashboard.html')

@role_required(User.DEPARTMENT)
def department_dashboard(request):
	return render(request, 'accounts/department_dashboard.html')

@role_required(User.LECTURER)
def lecturer_dashboard(request):
	return render(request, 'accounts/lecturer_dashboard.html')

@role_required(User.ADMIN)
def admin_dashboard(request):
	return render(request, 'accounts/admin_dashboard.html')

def forbidden_view(request):
	return render(request, 'accounts/forbidden.html', status=403)

def logout_view(request):
	logout(request)
	return redirect('login')
