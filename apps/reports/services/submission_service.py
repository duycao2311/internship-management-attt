from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.reports.models import WeeklyDeadline, FinalDeadline, TermConfig


def submit_weekly(report, user):
    """
    Logic nộp bài tuần:
    - Nếu is_locked → reject (ValidationError)
    - Else:
        is_submitted = True
        is_locked = True
        submitted_at = now()
        Nếu now > deadline → is_late = True
    """
    if report.is_locked:
        raise ValidationError("Báo cáo tuần này đã bị khóa. Không thể nộp lại.")

    now = timezone.now()
    report.is_submitted = True
    report.is_locked = True
    report.submitted_at = now

    # Kiểm tra deadline
    term = report.assignment.term
    if term:
        try:
            weekly_dl = WeeklyDeadline.objects.get(term=term, week_number=report.week_number)
            if now > weekly_dl.deadline:
                report.is_late = True
            else:
                report.is_late = False
        except WeeklyDeadline.DoesNotExist:
            report.is_late = False
    else:
        report.is_late = False

    report.save(update_fields=[
        'is_submitted', 'is_locked', 'submitted_at', 'is_late',
        'title', 'content',
    ])

    return report


def submit_final(report, user):
    """
    Logic nộp báo cáo tổng kết:
    1. Kiểm tra min_required_weeks (từ TermConfig)
    2. Nếu is_locked → reject
    3. Else: submit giống weekly
    """
    if report.is_locked:
        raise ValidationError("Báo cáo tổng kết đã bị khóa. Không thể nộp lại.")

    # Kiểm tra min_required_weeks
    assignment = report.assignment
    term = assignment.term

    if term:
        try:
            config = TermConfig.objects.get(term=term)
            min_weeks = config.min_required_weeks
        except TermConfig.DoesNotExist:
            min_weeks = 5  # Fallback default
    else:
        min_weeks = 5

    submitted_count = assignment.weekly_reports.filter(is_submitted=True).count()
    if submitted_count < min_weeks:
        raise ValidationError(
            f"Bạn cần nộp ít nhất {min_weeks} báo cáo tuần trước khi nộp báo cáo tổng kết. "
            f"Hiện tại đã nộp: {submitted_count} tuần."
        )

    now = timezone.now()
    report.is_submitted = True
    report.is_locked = True
    report.submitted_at = now

    # Kiểm tra deadline
    if term:
        try:
            final_dl = FinalDeadline.objects.get(term=term)
            if now > final_dl.deadline:
                report.is_late = True
            else:
                report.is_late = False
        except FinalDeadline.DoesNotExist:
            report.is_late = False
    else:
        report.is_late = False

    report.save(update_fields=[
        'is_submitted', 'is_locked', 'submitted_at', 'is_late',
        'title', 'content',
    ])

    return report


def unlock_report(report):
    """
    Lecturer / Admin mở khóa report để SV nộp lại.
    Reset is_locked = False, is_submitted = False.
    """
    report.is_locked = False
    report.is_submitted = False
    report.save(update_fields=['is_locked', 'is_submitted'])
    return report
