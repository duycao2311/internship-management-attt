from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from apps.accounts.decorators import role_required
from .models import InternshipPost, CV, Application, ExternalInternshipRequest
from .forms import InternshipPostForm, CVUploadForm, ApplicationForm, ExternalInternshipRequestForm
from apps.reports.models import InternshipAssignment, DepartmentLecturerAssignment, InternshipTerm
from apps.reports.services.assignment_service import setup_assignment_foundation

# ----------------- DEPARTMENT VIEWS ----------------- #

@role_required(['department'])
def post_list(request):
    """View cho Department xem danh sách tin tuyển dụng của chính họ"""
    posts = InternshipPost.objects.filter(department=request.user.department_profile).order_by('-created_at')
    return render(request, 'recruitment/post_list.html', {'posts': posts})

@role_required(['department'])
def post_create(request):
    """View cho Department tạo tin tuyển dụng mới"""
    if request.method == 'POST':
        form = InternshipPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.department = request.user.department_profile
            post.save()
            messages.success(request, 'Tạo tin tuyển dụng thành công!')
            return redirect('recruitment:department_post_list')
    else:
        form = InternshipPostForm()
    return render(request, 'recruitment/post_form.html', {'form': form, 'title': 'Tạo tin tuyển dụng mới'})

@role_required(['department'])
def post_update(request, pk):
    """View cho Department sửa tin tuyển dụng"""
    post = get_object_or_404(InternshipPost, pk=pk, department=request.user.department_profile)
    if request.method == 'POST':
        form = InternshipPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật tin tuyển dụng thành công!')
            return redirect('recruitment:department_post_list')
    else:
        form = InternshipPostForm(instance=post)
    return render(request, 'recruitment/post_form.html', {'form': form, 'title': 'Chỉnh sửa tin tuyển dụng'})

@role_required(['department'])
def post_delete(request, pk):
    """View cho Department xoá tin"""
    post = get_object_or_404(InternshipPost, pk=pk, department=request.user.department_profile)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Xoá tin tuyển dụng thành công!')
        return redirect('recruitment:department_post_list')
    return render(request, 'recruitment/post_confirm_delete.html', {'post': post})

@role_required(['department'])
def department_application_list(request):
    """View cho Department xem danh sách hồ sơ ứng tuyển"""
    # Chỉ lấy các application nộp vào các post của Department này
    applications = Application.objects.filter(post__department=request.user.department_profile).order_by('-applied_at')
    
    # Lọc theo trạng thái
    status_filter = request.GET.get('status')
    if status_filter in dict(Application.STATUS_CHOICES).keys():
        applications = applications.filter(status=status_filter)
        
    return render(request, 'recruitment/department_application_list.html', {
        'applications': applications,
        'current_status': status_filter
    })

@role_required(['department'])
def department_application_detail(request, pk):
    """View cho Department xem chi tiết hồ sơ"""
    application = get_object_or_404(Application, pk=pk, post__department=request.user.department_profile)
    has_assignment = hasattr(application, 'assignment')
    return render(request, 'recruitment/department_application_detail.html', {
        'application': application,
        'has_assignment': has_assignment
    })

@role_required(['department'])
def department_application_status(request, pk, status):
    """View cập nhật trạng thái phê duyệt (Chấp nhận / Từ chối)"""
    application = get_object_or_404(Application, pk=pk, post__department=request.user.department_profile)
    
    if request.method == 'POST' and status in ['accepted', 'rejected']:
        has_assignment = hasattr(application, 'assignment')
        if has_assignment:
            messages.error(request, 'Không thể thay đổi quyết định! Sinh viên đã xác nhận thực tập chính thức.')
        elif application.status == 'rejected':
            messages.error(request, 'Hồ sơ đã bị từ chối trước đó, quyết định đã bị khóa.')
        elif application.status == status:
            pass # No change needed
        else:
            application.status = status
            application.save()
            messages.success(request, f'Đã cập nhật trạng thái hồ sơ thành viên {application.student.user.username} !')
    
    return redirect('recruitment:department_application_detail', pk=pk)

# ----------------- STUDENT VIEWS ----------------- #

@role_required(['student'])
def student_post_list(request):
    """View cho Student xem danh sách các tin TĐ đang mở"""
    today = timezone.now().date()
    posts = InternshipPost.objects.filter(
        Q(status='open'),
        Q(deadline__gte=today) | Q(deadline__isnull=True)
    ).select_related('department').order_by('-created_at')
    return render(request, 'recruitment/student_post_list.html', {'posts': posts})

@role_required(['student'])
def student_post_detail(request, pk):
    """View cho Student xem chi tiết 1 tin TĐ"""
    post = get_object_or_404(InternshipPost.objects.select_related('department'), pk=pk)
    # Check if student already applied
    has_applied = Application.objects.filter(post=post, student=request.user.student_profile).exists()
    return render(request, 'recruitment/student_post_detail.html', {'post': post, 'has_applied': has_applied})

@role_required(['student'])
def student_cv_list(request):
    """View cho Student quản lý CV của mình"""
    cvs = CV.objects.filter(student=request.user.student_profile).order_by('-updated_at')
    if request.method == 'POST':
        form = CVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            cv = form.save(commit=False)
            cv.student = request.user.student_profile
            cv.save()
            messages.success(request, 'Tải lên CV thành công!')
            return redirect('recruitment:student_cv_list')
    else:
        form = CVUploadForm()
    return render(request, 'recruitment/student_cv_list.html', {'cvs': cvs, 'form': form})

@role_required(['student'])
def student_apply(request, pk):
    """View xử lý việc sinh viên chọn CV và apply"""
    post = get_object_or_404(InternshipPost, pk=pk)
    if not post.is_active():
        messages.error(request, 'Tin tuyển dụng này đã đóng hoặc hết hạn!')
        return redirect('recruitment:student_post_detail', pk=pk)
        
    if Application.objects.filter(post=post, student=request.user.student_profile).exists():
        messages.warning(request, 'Bạn đã ứng tuyển vị trí này rồi!')
        return redirect('recruitment:student_post_detail', pk=pk)
        
    if request.method == 'POST':
        form = ApplicationForm(request.POST, student_profile=request.user.student_profile)
        if form.is_valid():
            application = form.save(commit=False)
            application.post = post
            application.student = request.user.student_profile
            application.save()
            messages.success(request, 'Nộp đơn ứng tuyển thành công!')
            return redirect('recruitment:student_application_list')
    else:
        form = ApplicationForm(student_profile=request.user.student_profile)
        
    return render(request, 'recruitment/student_apply.html', {'form': form, 'post': post})

@role_required(['student'])
def student_application_list(request):
    """View cho Student xem danh sách ứng tuyển"""
    applications = Application.objects.filter(
        student=request.user.student_profile
    ).select_related(
        'post__department', 'cv', 'assignment'
    ).order_by('-applied_at')
    external_requests = ExternalInternshipRequest.objects.filter(student=request.user.student_profile).order_by('-created_at')
    return render(request, 'recruitment/student_application_list.html', {
        'applications': applications,
        'external_requests': external_requests
    })

@role_required(['student'])
def student_confirm_placement(request, pk):
    """View cho Student xác nhận 1 vị trí thực tập duy nhất."""
    application = get_object_or_404(Application, pk=pk, student=request.user.student_profile, status='accepted')
    
    # Check if student already has an active assignment
    existing = InternshipAssignment.objects.filter(
        Q(application__student=request.user.student_profile, is_active=True) |
        Q(external_request__student=request.user.student_profile, is_active=True)
    ).first()
    if existing:
        messages.error(request, 'Bạn đã chốt một điểm thực tập rồi! Không thể chọn thêm.')
        return redirect('recruitment:student_application_list')
        
    if request.method == 'POST':
        # Auto-assignment logic
        try:
            mapping = DepartmentLecturerAssignment.objects.get(department=application.post.department)
            assigned_lecturer = mapping.lecturer
        except DepartmentLecturerAssignment.DoesNotExist:
            assigned_lecturer = None

        # Resolve active term timeframe
        active_period = InternshipTerm.objects.filter(is_active=True).first()
        period_start = active_period.start_date if active_period else None
        period_end = active_period.end_date if active_period else None

        assignment = InternshipAssignment.objects.create(
            application=application,
            lecturer=assigned_lecturer,
            term=active_period,
            start_date=period_start,
            end_date=period_end,
            is_active=True
        )
        setup_assignment_foundation(assignment)
        messages.success(request, 'Xác nhận điểm thực tập thành công! Bạn có thể bắt đầu theo dõi tiến độ báo cáo.')
        return redirect('student_dashboard')
        
    return render(request, 'recruitment/student_confirm_placement.html', {'application': application})

@role_required(['student'])
def student_external_request_create(request):
    """View cho Sinh viên nộp đơn Thực tập ngoài"""
    
    # Check assignment presence
    existing = InternshipAssignment.objects.filter(
        Q(application__student=request.user.student_profile, is_active=True) |
        Q(external_request__student=request.user.student_profile, is_active=True)
    ).first()
    
    if existing:
        messages.error(request, 'Bạn đã có điểm thực tập chính thức trên hệ thống!')
        return redirect('student_dashboard')

    # Prevent multiple pending requests
    pending = ExternalInternshipRequest.objects.filter(student=request.user.student_profile, status='pending').first()
    if pending:
        messages.warning(request, 'Bạn đang có một yêu cầu thực tập ngoài chờ phê duyệt, không thể nộp thêm!')
        return redirect('recruitment:student_application_list')

    if request.method == 'POST':
        form = ExternalInternshipRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.student = request.user.student_profile
            req.save()
            messages.success(request, 'Đã gửi yêu cầu Thực tập ngoài thành công! Trạng thái: Chờ phê duyệt.')
            return redirect('recruitment:student_application_list')
    else:
        form = ExternalInternshipRequestForm()

    return render(request, 'recruitment/student_external_form.html', {'form': form})

