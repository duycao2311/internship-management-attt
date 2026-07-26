import datetime
from apps.reports.models import InternshipTerm


def create_default_term(year, start_month=6, start_day=20, duration_weeks=10):
    """
    Tạo kỳ thực tập mặc định cho năm.
    start_date = 20/06/year, end_date = +10 tuần.
    Nếu đã tồn tại (cùng year) thì trả về term hiện có.
    """
    start_date = datetime.date(year, start_month, start_day)
    end_date = start_date + datetime.timedelta(weeks=duration_weeks)

    term, created = InternshipTerm.objects.get_or_create(
        year=year,
        defaults={
            'start_date': start_date,
            'end_date': end_date,
            'is_active': False,
        }
    )
    return term


def set_active_term(term):
    """
    Đặt term này là active, tắt tất cả term khác.
    """
    InternshipTerm.objects.filter(is_active=True).exclude(pk=term.pk).update(is_active=False)
    term.is_active = True
    term.save(update_fields=['is_active', 'name'])


def get_active_term():
    """Helper: lấy kỳ thực tập đang active."""
    return InternshipTerm.get_active()
