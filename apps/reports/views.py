from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.accounts.decorators import role_required
from apps.accounts.models import LecturerProfile
from .models import InternshipAssignment, WeeklyReport, FinalReport, LecturerFeedback
from .forms import WeeklyReportForm, FinalReportForm, LecturerFeedbackForm

def get_student_assignment(request):
    """Lấy assignment của student đang đăng nhập. Nếu không có trả về None"""
    from django.db.models import Q
    return InternshipAssignment.objects.filter(
        Q(application__student=request.user.student_profile, is_active=True) |
        Q(external_request__student=request.user.student_profile, is_active=True)
    ).first()

@role_required(['student'])
def student_dashboard(request):
    """Màn hình tổng quan tiến độ của sinh viên"""
    assignment = get_student_assignment(request)
    if not assignment:
        return render(request, 'reports/student_no_assignment.html')
        
    weekly_count = assignment.weekly_reports.count()
    has_final = hasattr(assignment, 'final_report')
    
    return render(request, 'reports/student_dashboard.html', {
        'assignment': assignment,
        'weekly_count': weekly_count,
        'has_final': has_final
    })

@role_required(['student'])
def weekly_report_list(request):
    """Danh sách báo cáo hàng tuần"""
    assignment = get_student_assignment(request)
    if not assignment:
        return render(request, 'reports/student_no_assignment.html')
        
    reports = assignment.weekly_reports.all()
    return render(request, 'reports/weekly_report_list.html', {'reports': reports, 'assignment': assignment})

@role_required(['student'])
def weekly_report_create(request):
    """Nộp báo cáo tuần mới"""
    assignment = get_student_assignment(request)
    if not assignment:
        return render(request, 'reports/student_no_assignment.html')
        
    last_report = assignment.weekly_reports.order_by('-week_number').first()
    if last_report and not hasattr(last_report, 'feedback'):
        messages.error(request, f'Bạn không thể nộp thêm! Báo cáo Tuần {last_report.week_number} của bạn vẫn đang chờ Giảng viên nhận xét.')
        return redirect('reports:weekly_report_list')
        
    if request.method == 'POST':
        form = WeeklyReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.assignment = assignment
            report.save()
            messages.success(request, f'Đã nộp báo cáo tuần {report.week_number} thành công!')
            return redirect('reports:weekly_report_list')
    else:
        # Gợi ý số tuần tiếp theo tự động
        next_week = assignment.weekly_reports.count() + 1
        form = WeeklyReportForm(initial={'week_number': next_week})
        
    return render(request, 'reports/weekly_report_form.html', {'form': form, 'assignment': assignment})

@role_required(['student'])
def final_report_detail(request):
    """Xem hoặc nộp báo cáo tổng kết"""
    assignment = get_student_assignment(request)
    if not assignment:
        return render(request, 'reports/student_no_assignment.html')
        
    # Đoạn này xử lý xem hay tạo báo cáo
    if hasattr(assignment, 'final_report'):
        return render(request, 'reports/final_report_detail.html', {'report': assignment.final_report, 'assignment': assignment})
        
    # Tạo mới bản báo cáo tổng kết
    if request.method == 'POST':
        form = FinalReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.assignment = assignment
            report.save()
            messages.success(request, 'Đã hoàn tất nộp báo cáo tổng kết đợt thực tập!')
            return redirect('reports:final_report_detail')
    else:
        form = FinalReportForm()
        
    return render(request, 'reports/final_report_form.html', {'form': form, 'assignment': assignment})

# ----------------- LECTURER VIEWS ----------------- #

@role_required(['lecturer'])
def lecturer_dashboard(request):
    """View cho Giảng viên xem danh sách các Sinh viên đang phụ trách kèm Thống kê"""
    from django.db.models import Count
    
    lecturer_profile, _ = LecturerProfile.objects.get_or_create(user=request.user)
    assignments = InternshipAssignment.objects.filter(lecturer=lecturer_profile).order_by('-start_date')
    
    total_students = assignments.count()
    
    weekly_reports = WeeklyReport.objects.filter(assignment__lecturer=lecturer_profile)
    total_weekly = weekly_reports.count()
    weekly_waiting = weekly_reports.filter(feedback__isnull=True).count()
    
    final_reports = FinalReport.objects.filter(assignment__lecturer=lecturer_profile)
    total_final = final_reports.count()
    final_waiting = final_reports.filter(feedback__isnull=True).count()
    
    students_no_reports = assignments.annotate(num_weekly=Count('weekly_reports')).filter(num_weekly=0).count()
    
    context = {
        'assignments': assignments,
        'metrics': {
            'total_students': total_students,
            'total_weekly': total_weekly,
            'weekly_waiting': weekly_waiting,
            'total_final': total_final,
            'final_waiting': final_waiting,
            'students_no_reports': students_no_reports,
            'total_waiting': weekly_waiting + final_waiting
        }
    }
    
    return render(request, 'reports/lecturer_dashboard.html', context)

@role_required(['lecturer'])
def lecturer_student_detail(request, assignment_id):
    """Xem toàn bộ diễn biến lịch sử báo cáo của 1 Sinh viên duy nhất, đính kèm form Feedback"""
    lecturer_profile, _ = LecturerProfile.objects.get_or_create(user=request.user)
    assignment = get_object_or_404(InternshipAssignment, id=assignment_id, lecturer=lecturer_profile)
    weekly_reports = assignment.weekly_reports.all()
    # Khởi tạo sãn đối tượng Form nháp rỗng để template tái sử dụng loop
    feedback_form = LecturerFeedbackForm()
    
    return render(request, 'reports/lecturer_student_detail.html', {
        'assignment': assignment,
        'weekly_reports': weekly_reports,
        'feedback_form': feedback_form
    })

@role_required(['lecturer'])
def lecturer_feedback_create(request, report_type, report_id):
    """POST Router đa năng xử lý lưu Feedback vào CSDL"""
    if request.method == 'POST':
        lecturer_profile, _ = LecturerProfile.objects.get_or_create(user=request.user)
        # Tuỳ theo Loại Request (Weekly / Final) mà quăng ID tới khóa ngoại tương ứng
        if report_type == 'weekly':
            report = get_object_or_404(WeeklyReport, id=report_id, assignment__lecturer=lecturer_profile)
            feedback, created = LecturerFeedback.objects.get_or_create(weekly_report=report)
        elif report_type == 'final':
            report = get_object_or_404(FinalReport, id=report_id, assignment__lecturer=lecturer_profile)
            feedback, created = LecturerFeedback.objects.get_or_create(final_report=report)
        else:
            return redirect('reports:lecturer_dashboard')
            
        form = LecturerFeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lưu nhận xét thành công cho {report.title}!')
            return redirect('reports:lecturer_student_detail', assignment_id=report.assignment.id)
            
    return redirect('reports:lecturer_dashboard')

