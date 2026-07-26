from django.db import transaction
from apps.reports.models import InternshipTerm
from apps.reports.services.mentor_group_service import get_assignment_department, assign_mentor_group_for_assignment


@transaction.atomic
def setup_assignment_foundation(assignment):
    """
    Setup các thông số cơ bản cho một assignment mới:
    - Term, dates, department, mentor_group.
    Lưu ý: 10 WeeklyReport + 1 FinalReport được tạo tự động qua signal (post_save).
    """
    # 1. Gán Term nếu chưa có
    if not assignment.term:
        active_term = InternshipTerm.get_active()
        if active_term:
            assignment.term = active_term

    # Nếu vẫn không có term thì không thể tiếp tục setup an toàn
    if not assignment.term:
        return assignment

    # 2. Gán start_date, end_date theo term
    if not assignment.start_date:
        assignment.start_date = assignment.term.start_date
    if not assignment.end_date:
        assignment.end_date = assignment.term.end_date

    # 3. Gán department
    if not assignment.department:
        dept = get_assignment_department(assignment)
        if dept:
            assignment.department = dept

    assignment.save(update_fields=['term', 'start_date', 'end_date', 'department'])

    # 4. Gán mentor group
    if assignment.department:
        try:
            assign_mentor_group_for_assignment(assignment)
        except Exception:
            pass

    return assignment


@transaction.atomic
def change_assignment_department(assignment, new_department, new_lecturer=None):
    """
    Đổi doanh nghiệp cho một assignment đang tồn tại.
    Phải reset mentor_group.
    """
    assignment.department = new_department

    if new_lecturer is not None:
        assignment.lecturer = new_lecturer

    # Xoá liên kết mentor group cũ
    assignment.mentor_group = None
    assignment.save(update_fields=['department', 'lecturer', 'mentor_group'])

    # Gán lại mentor group mới cho department mới
    try:
        assign_mentor_group_for_assignment(assignment)
    except Exception:
        pass

    return assignment
