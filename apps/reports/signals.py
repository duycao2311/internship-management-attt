from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import InternshipAssignment, WeeklyReport, FinalReport


@receiver(post_save, sender=InternshipAssignment)
def create_reports_for_assignment(sender, instance, created, **kwargs):
    """
    Khi Assignment được tạo mới:
    → auto tạo 10 WeeklyReport (week 1 → 10) + 1 FinalReport
    Tất cả đều is_submitted=False, is_locked=False.
    """
    if not created:
        return

    # Tạo 10 WeeklyReport
    weekly_reports = []
    for week in range(1, 11):
        weekly_reports.append(
            WeeklyReport(
                assignment=instance,
                week_number=week,
                is_submitted=False,
                is_locked=False,
            )
        )
    WeeklyReport.objects.bulk_create(weekly_reports, ignore_conflicts=True)

    # Tạo 1 FinalReport
    FinalReport.objects.get_or_create(
        assignment=instance,
        defaults={
            'is_submitted': False,
            'is_locked': False,
        }
    )
