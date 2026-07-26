from django.db.models import Q
from apps.reports.models import InternshipAssignment
from apps.reports.services.grading_service import calculate_assignment_score

def resolve_assignment_student(assignment):
    """
    Helper giải quyết lỗi lấy thông tin sinh viên từ assignment an toàn.
    Tránh crash nếu model thiếu field.
    """
    # Lấy từ application (Thực tập nội bộ)
    application = getattr(assignment, 'application', None)
    if application:
        student = getattr(application, 'student', None)
        if student: return student
        student_profile = getattr(application, 'student_profile', None)
        if student_profile: return student_profile
        user = getattr(application, 'user', None)
        if user: return user

    # Lấy từ external_request (Thực tập ngoài)
    external_req = getattr(assignment, 'external_request', None)
    if external_req:
        student = getattr(external_req, 'student', None)
        if student: return student
        student_profile = getattr(external_req, 'student_profile', None)
        if student_profile: return student_profile
        user = getattr(external_req, 'user', None)
        if user: return user

    return None

def build_statistics_context(
    period=None,
    department=None,
    lecturer=None,
    mentor=None,
    pass_status=None,
    issue_status=None
):
    """
    Xây dựng context thống kê toàn cục cho màn hình Thống kê (Phần 3).
    Param 'period' thực tế là InternshipTerm object (giữ tên param cho backward compat với views).
    """
    # 1. Query Assignment bắt đầu từ term
    # CHỈ LẤY assignment ĐANG ACTIVE để tránh tính trùng sinh viên đổi chỗ thực tập
    assignments_qs = InternshipAssignment.objects.filter(
        is_active=True
    ).select_related(
        'term',
        'lecturer',
        'mentor_group'
    ).prefetch_related(
        'application',
        'external_request',
        'weekly_reports', 'weekly_reports__grades',
        'final_report', 'final_report__grades'
    )

    # 2. Áp dụng các bộ lọc (Filters)
    if period:
        assignments_qs = assignments_qs.filter(term=period)

    if department:
        # Search text theo tên doanh nghiệp
        assignments_qs = assignments_qs.filter(
            Q(application__post__department__organization_name__icontains=department) |
            Q(application__post__department__user__username__icontains=department) |
            Q(external_request__company_name__icontains=department)
        )

    if lecturer:
        if isinstance(lecturer, int) or (isinstance(lecturer, str) and lecturer.isdigit()):
            assignments_qs = assignments_qs.filter(lecturer_id=lecturer)
        else:
            assignments_qs = assignments_qs.filter(lecturer=lecturer)

    if mentor:
        if isinstance(mentor, int) or (isinstance(mentor, str) and mentor.isdigit()):
            assignments_qs = assignments_qs.filter(mentor_group__mentor_id=mentor)
        else:
            assignments_qs = assignments_qs.filter(mentor_group__mentor=mentor)

    # 3. Chuẩn bị biến lưu trữ kết quả
    rows = []
    passed_count = 0
    failed_count = 0
    mentor_ungraded_count = 0
    lecturer_ungraded_count = 0
    total_missing_weeks = 0
    total_late_submissions = 0

    # 4. Duyệt qua từng assignment để tính toán
    for assignment in assignments_qs:
        try:
            score_info = calculate_assignment_score(assignment)
            if not isinstance(score_info, dict):
                score_info = {}
        except Exception:
            score_info = {}

        total_score = score_info.get('total_score', 0)
        is_passed = score_info.get('is_passed', False)
        details = score_info.get('details', {})
        if not isinstance(details, dict):
            details = {}

        # Lấy điểm chi tiết an toàn
        avg_weekly_mentor = details.get('avg_weekly_mentor', 0)
        avg_weekly_lecturer = details.get('avg_weekly_lecturer', 0)

        # Tính điểm trung bình cộng thô
        weekly_average = (float(avg_weekly_mentor) + float(avg_weekly_lecturer)) / 2

        final_report = getattr(assignment, 'final_report', None)
        if final_report:
            final_mentor = details.get('final_mentor_score', 0)
            final_lecturer = details.get('final_lecturer_score', 0)
            final_score = (float(final_mentor) + float(final_lecturer)) / 2
        else:
            final_score = None

        # Bộ lọc trạng thái Đạt/Chưa đạt
        if pass_status == 'passed' and not is_passed:
            continue
        if pass_status == 'failed' and is_passed:
            continue

        if is_passed:
            passed_count += 1
        else:
            failed_count += 1

        # Thống kê bài tập (Missing & Late)
        weekly_reports = list(assignment.weekly_reports.all())

        # Đếm số tuần thiếu (chưa nộp)
        submitted_weeks = set(r.week_number for r in weekly_reports if getattr(r, 'is_submitted', False))
        missing_week_count = max(0, 10 - len(submitted_weeks))

        # Đếm số bài nộp muộn
        late_submission_count = sum(1 for r in weekly_reports if getattr(r, 'is_late', False))
        if final_report and getattr(final_report, 'is_late', False):
            late_submission_count += 1

        # Đếm bài chưa chấm
        row_mentor_ungraded = 0
        row_lecturer_ungraded = 0
        for r in weekly_reports:
            if r.is_submitted:
                mentor_graded = any(g.grader_type == 'mentor' for g in r.grades.all())
                if not mentor_graded:
                    row_mentor_ungraded += 1

                lecturer_graded = any(g.grader_type == 'lecturer' for g in r.grades.all())
                if not lecturer_graded:
                    row_lecturer_ungraded += 1

        if final_report and final_report.is_submitted:
            mentor_graded = any(g.grader_type == 'mentor' for g in final_report.grades.all())
            if not mentor_graded:
                row_mentor_ungraded += 1

            lecturer_graded = any(g.grader_type == 'lecturer' for g in final_report.grades.all())
            if not lecturer_graded:
                row_lecturer_ungraded += 1

        # Áp dụng bộ lọc issue_status
        has_no_final = not final_report or not final_report.is_submitted
        if issue_status == 'missing_weeks' and missing_week_count == 0:
            continue
        if issue_status == 'late_submissions' and late_submission_count == 0:
            continue
        if issue_status == 'mentor_ungraded' and row_mentor_ungraded == 0:
            continue
        if issue_status == 'lecturer_ungraded' and row_lecturer_ungraded == 0:
            continue
        if issue_status == 'no_final_report' and not has_no_final:
            continue

        mentor_ungraded_count += row_mentor_ungraded
        lecturer_ungraded_count += row_lecturer_ungraded
        total_missing_weeks += missing_week_count
        total_late_submissions += late_submission_count

        # Lấy student thông qua helper an toàn
        student = resolve_assignment_student(assignment)

        # Logic đánh giá rủi ro (Risk Level)
        risk_level = 'normal'
        risk_label = 'Bình thường'
        if missing_week_count >= 5 or (isinstance(total_score, (int, float)) and total_score < 4):
            risk_level = 'high'
            risk_label = 'Nguy cơ cao'
        elif late_submission_count > 0 or (1 <= missing_week_count <= 4):
            risk_level = 'medium'
            risk_label = 'Cần lưu ý'

        rows.append({
            'student': student,
            'company': assignment.get_company_name,
            'lecturer': assignment.lecturer,
            'mentor': assignment.mentor_group.mentor if getattr(assignment, 'mentor_group', None) else None,
            'mentor_group': getattr(assignment, 'mentor_group', None),
            'weekly_average': round(weekly_average, 2),
            'final_score': round(final_score, 2) if final_score is not None else None,
            'total_score': total_score,
            'is_passed': is_passed,
            'missing_week_count': missing_week_count,
            'late_submission_count': late_submission_count,
            'assignment': assignment,
            'risk_level': risk_level,
            'risk_label': risk_label,
        })

    total_students = len(rows)
    pass_rate = round((passed_count / total_students * 100), 2) if total_students > 0 else 0

    return {
        'rows': rows,
        'cards': {
            'total_students': total_students,
            'passed_count': passed_count,
            'failed_count': failed_count,
            'pass_rate': pass_rate,
            'mentor_ungraded_count': mentor_ungraded_count,
            'lecturer_ungraded_count': lecturer_ungraded_count,
            'total_missing_weeks': total_missing_weeks,
            'total_late_submissions': total_late_submissions,
        }
    }
