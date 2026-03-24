from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User, StudentProfile, DepartmentProfile, LecturerProfile
from .forms import StudentProfileForm, DepartmentProfileForm, LecturerProfileForm
from .views import role_required

@login_required
def profile_redirect(request):
    if request.user.role == User.STUDENT:
        return redirect('student_profile')
    elif request.user.role == User.DEPARTMENT:
        return redirect('department_profile')
    elif request.user.role == User.LECTURER:
        return redirect('lecturer_profile')
    else:
        return redirect('dashboard')

@role_required(User.STUDENT)
def student_profile(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=profile)
    return render(request, 'accounts/student_profile.html', {'form': form})

@role_required(User.DEPARTMENT)
def department_profile(request):
    profile, _ = DepartmentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = DepartmentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('department_profile')
    else:
        form = DepartmentProfileForm(instance=profile)
    return render(request, 'accounts/department_profile.html', {'form': form})

@role_required(User.LECTURER)
def lecturer_profile(request):
    profile, _ = LecturerProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = LecturerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('lecturer_profile')
    else:
        form = LecturerProfileForm(instance=profile)
    return render(request, 'accounts/lecturer_profile.html', {'form': form})
