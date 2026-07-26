import datetime
from django.utils import timezone
from django.db import transaction
from apps.reports.models import WeeklyDeadline, FinalDeadline


def get_sunday_of_week(date_obj):
    """
    Trả về datetime timezone-aware của ngày Chủ nhật trong cùng tuần với date_obj lúc 23:59:59.
    (Monday = 0, Sunday = 6)
    """
    days_to_sunday = 6 - date_obj.weekday()
    sunday = date_obj + datetime.timedelta(days=days_to_sunday)
    dt_naive = datetime.datetime.combine(sunday, datetime.time(23, 59, 59))
    if timezone.is_naive(dt_naive):
        return timezone.make_aware(dt_naive)
    return dt_naive


@transaction.atomic
def generate_weekly_deadlines(term):
    """
    Sinh 10 WeeklyDeadline + 1 FinalDeadline cho term.
    Default deadline = Chủ nhật cuối mỗi tuần.
    Nếu đã có thì update (giữ nguyên nếu admin đã chỉnh).
    """
    start_date = term.start_date

    for week_num in range(1, 11):
        # Deadline tuần N = Chủ nhật cuối tuần N (tính từ start_date)
        week_start = start_date + datetime.timedelta(weeks=week_num - 1)
        sunday_deadline = get_sunday_of_week(week_start)

        WeeklyDeadline.objects.update_or_create(
            term=term,
            week_number=week_num,
            defaults={
                'deadline': sunday_deadline,
            }
        )

    # Final deadline = Chủ nhật tuần 10
    final_week_start = start_date + datetime.timedelta(weeks=9)
    final_sunday = get_sunday_of_week(final_week_start)

    FinalDeadline.objects.update_or_create(
        term=term,
        defaults={
            'deadline': final_sunday,
        }
    )


def get_weekly_deadline(term, week_number):
    """Lấy deadline cho tuần cụ thể. Trả None nếu chưa có."""
    try:
        return WeeklyDeadline.objects.get(term=term, week_number=week_number)
    except WeeklyDeadline.DoesNotExist:
        return None


def get_final_deadline(term):
    """Lấy deadline cho final. Trả None nếu chưa có."""
    try:
        return FinalDeadline.objects.get(term=term)
    except FinalDeadline.DoesNotExist:
        return None


def update_weekly_deadline(term, week_number, new_deadline, changed_by=None):
    """Admin / Lecturer sửa deadline tuần."""
    dl, created = WeeklyDeadline.objects.get_or_create(
        term=term,
        week_number=week_number,
        defaults={'deadline': new_deadline, 'updated_by': changed_by}
    )
    if not created:
        dl.deadline = new_deadline
        dl.updated_by = changed_by
        dl.save(update_fields=['deadline', 'updated_by', 'updated_at'])
    return dl


def update_final_deadline(term, new_deadline, changed_by=None):
    """Admin / Lecturer sửa deadline final."""
    dl, created = FinalDeadline.objects.get_or_create(
        term=term,
        defaults={'deadline': new_deadline, 'updated_by': changed_by}
    )
    if not created:
        dl.deadline = new_deadline
        dl.updated_by = changed_by
        dl.save(update_fields=['deadline', 'updated_by', 'updated_at'])
    return dl
