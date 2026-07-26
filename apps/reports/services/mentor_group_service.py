from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count

from apps.accounts.models import MentorProfile
from apps.reports.models import MentorGroup
from apps.accounts.services import ensure_default_mentors


def get_assignment_department(assignment):
    """
    Xác định department từ assignment.
    """
    if assignment.department:
        return assignment.department

    # Fallback to application/post
    try:
        if assignment.application and assignment.application.post and assignment.application.post.department:
            return assignment.application.post.department
    except AttributeError:
        pass

    return None


@transaction.atomic
def assign_mentor_group_for_assignment(assignment):
    """
    Phân Mentor Group cho Assignment.
    """
    if not assignment.term:
        raise ValidationError("Assignment must have a term before assigning a mentor group.")

    department = get_assignment_department(assignment)
    if not department:
        raise ValidationError("Assignment must have an associated department.")

    # Gọi service tạo default mentors nếu chưa đủ
    ensure_default_mentors(department)

    # Tìm tất cả MentorGroup của department trong term này
    groups = MentorGroup.objects.filter(
        term=assignment.term,
        department=department,
        is_active=True
    ).annotate(
        current_members=Count('assignments')
    )

    # Lọc các group còn slot (current_members < capacity)
    available_groups = [g for g in groups if g.current_members < g.capacity]

    if available_groups:
        # Lấy group đầu tiên còn slot
        selected_group = available_groups[0]
    else:
        # Nếu tất cả các group đều đầy hoặc chưa có group nào, tạo group mới.
        # Tìm các mentor của department chưa có group trong term này.
        used_mentors = MentorGroup.objects.filter(
            term=assignment.term,
            department=department
        ).values_list('mentor_id', flat=True)

        available_mentors = MentorProfile.objects.filter(
            department=department
        ).exclude(id__in=used_mentors)

        if not available_mentors.exists():
            raise ValidationError("All mentors for this department are fully occupied for this term.")

        selected_mentor = available_mentors.first()

        # Tạo group mới
        group_count = MentorGroup.objects.filter(term=assignment.term, department=department).count()
        group_name = f"Nhóm Mentor {group_count + 1} - {department.organization_name}"

        selected_group = MentorGroup.objects.create(
            term=assignment.term,
            department=department,
            mentor=selected_mentor,
            name=group_name,
            capacity=10,
            is_active=True
        )

    assignment.mentor_group = selected_group
    assignment.department = department  # Ensure department is explicitly saved
    assignment.save(update_fields=['mentor_group', 'department'])

    return selected_group
