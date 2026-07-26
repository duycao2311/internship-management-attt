from django.core.exceptions import ValidationError
from decimal import Decimal
from apps.reports.models import WeeklyReportGrade, FinalReportGrade, WeeklyReport

def _validate_score(score):
    try:
        score = Decimal(str(score))
    except Exception:
        raise ValidationError("Score must be a valid number.")
    if score < 0 or score > 10:
        raise ValidationError("Score must be between 0 and 10.")
    return score

def grade_weekly_report_by_mentor(weekly_report, mentor_profile, score, comment=''):
    assignment = weekly_report.assignment
    if not assignment.mentor_group or assignment.mentor_group.mentor != mentor_profile:
        raise ValidationError("You do not have permission to grade this report as a mentor.")

    score = _validate_score(score)

    grade, created = WeeklyReportGrade.objects.update_or_create(
        weekly_report=weekly_report,
        grader_type='mentor',
        defaults={
            'mentor': mentor_profile,
            'lecturer': None,
            'score': score,
            'comment': comment
        }
    )
    return grade

def grade_weekly_report_by_lecturer(weekly_report, lecturer_profile, score, comment=''):
    assignment = weekly_report.assignment
    if assignment.lecturer != lecturer_profile:
        raise ValidationError("You do not have permission to grade this report as a lecturer.")

    score = _validate_score(score)

    grade, created = WeeklyReportGrade.objects.update_or_create(
        weekly_report=weekly_report,
        grader_type='lecturer',
        defaults={
            'lecturer': lecturer_profile,
            'mentor': None,
            'score': score,
            'comment': comment
        }
    )
    return grade

def grade_final_report_by_mentor(final_report, mentor_profile, score, comment=''):
    assignment = final_report.assignment
    if not assignment.mentor_group or assignment.mentor_group.mentor != mentor_profile:
        raise ValidationError("You do not have permission to grade this final report as a mentor.")

    score = _validate_score(score)

    grade, created = FinalReportGrade.objects.update_or_create(
        final_report=final_report,
        grader_type='mentor',
        defaults={
            'mentor': mentor_profile,
            'lecturer': None,
            'score': score,
            'comment': comment
        }
    )
    return grade

def grade_final_report_by_lecturer(final_report, lecturer_profile, score, comment=''):
    assignment = final_report.assignment
    if assignment.lecturer != lecturer_profile:
        raise ValidationError("You do not have permission to grade this final report as a lecturer.")

    score = _validate_score(score)

    grade, created = FinalReportGrade.objects.update_or_create(
        final_report=final_report,
        grader_type='lecturer',
        defaults={
            'lecturer': lecturer_profile,
            'mentor': None,
            'score': score,
            'comment': comment
        }
    )
    return grade

def calculate_assignment_score(assignment):
    """
    Tính điểm tổng kết cho Assignment.
    - Có 10 báo cáo tuần. Thiếu tuần = 0.
    - Weekly chiếm 50% (Mentor 50%, Lecturer 50%).
    - Final chiếm 50% (Mentor 50%, Lecturer 50%).
    - Chưa chấm = 0 điểm.
    KHÔNG cho nhập điểm tổng.
    """
    # 1. Tính điểm Weekly
    total_weekly_mentor = Decimal('0.0')
    total_weekly_lecturer = Decimal('0.0')

    weekly_reports = WeeklyReport.objects.filter(assignment=assignment)
    report_dict = {report.week_number: report for report in weekly_reports}

    # Duyệt qua 10 tuần
    for week_num in range(1, 11):
        report = report_dict.get(week_num)
        if report:
            mentor_grade = report.grades.filter(grader_type='mentor').first()
            if mentor_grade:
                total_weekly_mentor += mentor_grade.score

            lecturer_grade = report.grades.filter(grader_type='lecturer').first()
            if lecturer_grade:
                total_weekly_lecturer += lecturer_grade.score

    # Trung bình cộng điểm tuần (chia cho 10 tuần)
    avg_weekly_mentor = total_weekly_mentor / 10
    avg_weekly_lecturer = total_weekly_lecturer / 10

    # Điểm tuần cấu thành (Mentor 50%, Lecturer 50%)
    weekly_component = (avg_weekly_mentor * Decimal('0.5')) + (avg_weekly_lecturer * Decimal('0.5'))

    # 2. Tính điểm Final
    final_mentor_score = Decimal('0.0')
    final_lecturer_score = Decimal('0.0')

    if hasattr(assignment, 'final_report'):
        final_report = assignment.final_report
        mentor_grade = final_report.grades.filter(grader_type='mentor').first()
        if mentor_grade:
            final_mentor_score = mentor_grade.score

        lecturer_grade = final_report.grades.filter(grader_type='lecturer').first()
        if lecturer_grade:
            final_lecturer_score = lecturer_grade.score

    # Điểm final cấu thành (Mentor 50%, Lecturer 50%)
    final_component = (final_mentor_score * Decimal('0.5')) + (final_lecturer_score * Decimal('0.5'))

    # 3. Tính điểm tổng (Weekly 50%, Final 50%)
    total_score = (weekly_component * Decimal('0.5')) + (final_component * Decimal('0.5'))

    # Làm tròn 2 chữ số
    total_score = round(total_score, 2)

    is_passed = total_score >= Decimal('4.0')

    return {
        'total_score': total_score,
        'is_passed': is_passed,
        'details': {
            'avg_weekly_mentor': round(avg_weekly_mentor, 2),
            'avg_weekly_lecturer': round(avg_weekly_lecturer, 2),
            'weekly_component': round(weekly_component, 2),
            'final_mentor_score': round(final_mentor_score, 2),
            'final_lecturer_score': round(final_lecturer_score, 2),
            'final_component': round(final_component, 2)
        }
    }
