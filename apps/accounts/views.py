from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from apps.accounts.models import LecturerProfile, DepartmentProfile, StudentProfile
from apps.recruitment.models import InternshipPost, Application, ExternalInternshipRequest
from apps.reports.models import InternshipAssignment, WeeklyReport, DepartmentLecturerAssignment, InternshipPeriod, ExternalInternshipLecturerConfig
from apps.reports.forms import DepartmentLecturerAssignmentForm, InternshipPeriodForm, InternshipAssignmentForm, ExternalInternshipLecturerConfigForm
from django.shortcuts import get_object_or_404, redirect

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
	return redirect('reports:lecturer_dashboard')

@role_required(User.ADMIN)
def admin_dashboard(request):
	total_students = StudentProfile.objects.count()
	total_lecturers = LecturerProfile.objects.count()
	total_departments = DepartmentProfile.objects.count()
	total_posts = InternshipPost.objects.count()
	total_applications = Application.objects.count()
	total_assignments = InternshipAssignment.objects.filter(is_active=True).count()
	total_weekly_reports = WeeklyReport.objects.count()
	total_external_requests = ExternalInternshipRequest.objects.filter(status='pending').count()

	context = {
		'total_students': total_students,
		'total_lecturers': total_lecturers,
		'total_departments': total_departments,
		'total_posts': total_posts,
		'total_applications': total_applications,
		'total_assignments': total_assignments,
		'total_weekly_reports': total_weekly_reports,
		'total_external_requests': total_external_requests,
	}
	return render(request, 'accounts/admin_dashboard.html', context)

@role_required(User.ADMIN)
def admin_mapping_manager(request):
	mappings = DepartmentLecturerAssignment.objects.select_related('department', 'lecturer', 'lecturer__user').all()
	mapped_department_ids = mappings.values_list('department_id', flat=True)
	unassigned_departments = DepartmentProfile.objects.exclude(id__in=mapped_department_ids)
	
	context = {
		'mappings': mappings,
		'unassigned_departments': unassigned_departments,
	}
	return render(request, 'accounts/admin_mapping_manager.html', context)

@role_required(User.ADMIN)
def admin_mapping_create(request, department_id=None):
	initial = {}
	if department_id:
		initial['department'] = department_id

	if request.method == 'POST':
		form = DepartmentLecturerAssignmentForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Đã tạo phân công thành công.')
			return redirect('admin_mapping_manager')
	else:
		form = DepartmentLecturerAssignmentForm(initial=initial)
		
	context = {'form': form, 'action': 'Thêm mới Phân công'}
	return render(request, 'accounts/admin_mapping_form.html', context)

@role_required(User.ADMIN)
def admin_mapping_edit(request, mapping_id):
	mapping = get_object_or_404(DepartmentLecturerAssignment, id=mapping_id)
	if request.method == 'POST':
		form = DepartmentLecturerAssignmentForm(request.POST, instance=mapping)
		if form.is_valid():
			form.save()
			messages.success(request, 'Đã lưu thay đổi phân công.')
			return redirect('admin_mapping_manager')
	else:
		form = DepartmentLecturerAssignmentForm(instance=mapping)
		
	context = {'form': form, 'action': 'Chỉnh sửa Phân công', 'mapping': mapping}
	return render(request, 'accounts/admin_mapping_form.html', context)

@role_required(User.ADMIN)
def admin_mapping_delete(request, mapping_id):
	mapping = get_object_or_404(DepartmentLecturerAssignment, id=mapping_id)
	if request.method == 'POST':
		mapping.delete()
		messages.success(request, 'Đã xóa phân công giảng viên - doanh nghiệp.')
	return redirect('admin_mapping_manager')

@role_required(User.ADMIN)
def admin_period_manager(request):
	periods = InternshipPeriod.objects.all().order_by('-created_at')
	context = {'periods': periods}
	return render(request, 'accounts/admin_period_manager.html', context)

@role_required(User.ADMIN)
def admin_period_create(request):
	if request.method == 'POST':
		form = InternshipPeriodForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Đã tạo Kỳ thực tập thành công.')
			return redirect('admin_period_manager')
	else:
		form = InternshipPeriodForm()
	context = {'form': form, 'action': 'Tạo Mới Kỳ Thực Tập'}
	return render(request, 'accounts/admin_period_form.html', context)

@role_required(User.ADMIN)
def admin_period_edit(request, period_id):
	period = get_object_or_404(InternshipPeriod, id=period_id)
	if request.method == 'POST':
		form = InternshipPeriodForm(request.POST, instance=period)
		if form.is_valid():
			form.save()
			messages.success(request, 'Cập nhật Kỳ thực tập thành công.')
			return redirect('admin_period_manager')
	else:
		form = InternshipPeriodForm(instance=period)
	context = {'form': form, 'action': 'Chỉnh sửa Kỳ Thực Tập', 'period': period}
	return render(request, 'accounts/admin_period_form.html', context)

@role_required(User.ADMIN)
def admin_period_delete(request, period_id):
	period = get_object_or_404(InternshipPeriod, id=period_id)
	if request.method == 'POST':
		period.delete()
		messages.success(request, 'Đã xóa Kỳ thực tập.')
	return redirect('admin_period_manager')

@role_required(User.ADMIN)
def admin_period_toggle_active(request, period_id):
	period = get_object_or_404(InternshipPeriod, id=period_id)
	if request.method == 'POST':
		period.is_active = True
		period.save()
		messages.success(request, f'Đã kích hoạt khóa {period.name} làm hệ quy chiếu hiện tại.')
	return redirect('admin_period_manager')

@role_required(User.ADMIN)
def admin_assignment_manager(request):
	assignments = InternshipAssignment.objects.all().select_related('application__student__user', 'application__post__department', 'lecturer__user').order_by('-id')
	
	lecturer_id = request.GET.get('lecturer')
	department_id = request.GET.get('department')
	status = request.GET.get('status')
	
	if lecturer_id:
		if lecturer_id == 'none':
			assignments = assignments.filter(lecturer__isnull=True)
		else:
			assignments = assignments.filter(lecturer_id=lecturer_id)
			
	if department_id:
		assignments = assignments.filter(application__post__department_id=department_id)
		
	if status:
		if status == 'active':
			assignments = assignments.filter(is_active=True)
		elif status == 'inactive':
			assignments = assignments.filter(is_active=False)
			
	lecturers = LecturerProfile.objects.all()
	departments = DepartmentProfile.objects.all()

	context = {
		'assignments': assignments,
		'lecturers': lecturers,
		'departments': departments,
		'selected_lecturer': lecturer_id,
		'selected_department': department_id,
		'selected_status': status,
	}
	return render(request, 'accounts/admin_assignment_manager.html', context)

@role_required(User.ADMIN)
def admin_assignment_edit(request, assignment_id):
	assignment = get_object_or_404(InternshipAssignment, id=assignment_id)
	if request.method == 'POST':
		form = InternshipAssignmentForm(request.POST, instance=assignment)
		if form.is_valid():
			form.save()
			messages.success(request, 'Đã cập nhật phân công thực tập thành công.')
			return redirect('admin_assignment_manager')
	else:
		form = InternshipAssignmentForm(instance=assignment)
	context = {'form': form, 'assignment': assignment}
	return render(request, 'accounts/admin_assignment_form.html', context)

@role_required(User.ADMIN)
def admin_assignment_toggle_active(request, assignment_id):
	assignment = get_object_or_404(InternshipAssignment, id=assignment_id)
	if request.method == 'POST':
		assignment.is_active = not assignment.is_active
		assignment.save()
		status_text = "kích hoạt mở lại" if assignment.is_active else "tạm ngưng"
		student = assignment.get_student
		student_name = student.user.get_full_name() or student.user.username if student else "Unknown"
		messages.success(request, f'Đã {status_text} đợt thực tập của sinh viên {student_name}.')
	return redirect('admin_assignment_manager')

@role_required(User.ADMIN)
def admin_external_request_manager(request):
	status = request.GET.get('status', 'pending')
	requests = ExternalInternshipRequest.objects.all().order_by('-created_at')
	
	if status == 'pending':
		requests = requests.filter(status='pending')
	elif status == 'approved':
		requests = requests.filter(status='approved')
	elif status == 'rejected':
		requests = requests.filter(status='rejected')
		
	context = {
		'requests': requests,
		'current_status': status,
	}
	return render(request, 'accounts/admin_external_requests.html', context)

@role_required(User.ADMIN)
def admin_external_request_approve(request, req_id):
	req = get_object_or_404(ExternalInternshipRequest, id=req_id)
	if request.method == 'POST':
		action = request.POST.get('action')
		if action == 'approve' and req.status == 'pending':
			req.status = 'approved'
			req.save()
			
			# Lấy kỳ đang active
			try:
				active_period = InternshipPeriod.objects.get(is_active=True)
				period_start = active_period.start_date
				period_end = active_period.end_date
			except InternshipPeriod.DoesNotExist:
				period_start = None
				period_end = None
				
			# Tự động lấy giảng viên phụ trách nhóm thực tập ngoài nếu đã cấu hình
			external_config = ExternalInternshipLecturerConfig.get_solo()
			auto_lecturer = external_config.lecturer  # có thể là None nếu chưa cấu hình
				
			# Khởi tạo điểm thực tập
			InternshipAssignment.objects.create(
				external_request=req,
				lecturer=auto_lecturer,
				start_date=period_start,
				end_date=period_end,
				is_active=True
			)
			messages.success(request, f'Đã phê duyệt chức danh {req.position} cho sinh viên {req.student.user.username} và đã tạo đợt thực tập.')
		elif action == 'reject' and req.status == 'pending':
			req.status = 'rejected'
			req.note = request.POST.get('note', '')
			req.save()
			messages.info(request, f'Đã từ chối Đề xuất Thực tập ngoài của {req.student.user.username}.')
			
	return redirect('admin_external_request_manager')

@role_required(User.ADMIN)
def admin_external_lecturer_config(request):
	"""Cấu hình Giảng viên phụ trách Nhóm Thực tập Ngoài."""
	config = ExternalInternshipLecturerConfig.get_solo()
	
	if request.method == 'POST':
		form = ExternalInternshipLecturerConfigForm(request.POST, instance=config)
		if form.is_valid():
			form.save()
			
			# Backfill: gán giảng viên cho các external assignment đang có lecturer = null
			new_lecturer = form.cleaned_data.get('lecturer')
			if new_lecturer:
				backfill_count = InternshipAssignment.objects.filter(
					external_request__isnull=False,
					lecturer__isnull=True
				).update(lecturer=new_lecturer)
				if backfill_count > 0:
					messages.info(request, f'Đã tự động phân công Giảng viên cho {backfill_count} sinh viên Thực tập Ngoài đang chưa có GV.')
			
			messages.success(request, 'Đã lưu cấu hình Giảng viên phụ trách Nhóm Thực tập Ngoài.')
			return redirect('admin_external_lecturer_config')
	else:
		form = ExternalInternshipLecturerConfigForm(instance=config)
	
	context = {
		'config': config,
		'form': form,
	}
	return render(request, 'accounts/admin_external_lecturer_config.html', context)

def forbidden_view(request):
	return render(request, 'accounts/forbidden.html', status=403)

def logout_view(request):
	logout(request)
	return redirect('login')
