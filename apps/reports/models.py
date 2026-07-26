from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from apps.accounts.models import LecturerProfile, DepartmentProfile, MentorProfile
from apps.recruitment.models import Application

User = get_user_model()


# ==============================================================================
# 1. INTERNSHIP TERM (thay thế InternshipPeriod)
# ==============================================================================

class InternshipTerm(models.Model):
    """
    Kỳ thực tập. Mỗi năm chỉ có 1 kỳ, chỉ 1 kỳ active tại 1 thời điểm.
    Tên auto-generate: "Kỳ thực tập Hè năm {year}"
    """
    name = models.CharField(max_length=255, blank=True, help_text="Auto-generated")
    year = models.IntegerField(unique=True, help_text="Năm thực tập (unique)")
    start_date = models.DateField(help_text="Ngày bắt đầu thực tập")
    end_date = models.DateField(help_text="Ngày kết thúc thực tập")
    is_active = models.BooleanField(default=False, help_text="Chỉ 1 kỳ active tại 1 thời điểm")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year']
        verbose_name = "Kỳ thực tập"
        verbose_name_plural = "Kỳ thực tập"

    def save(self, *args, **kwargs):
        # Auto-generate name
        self.name = f"Kỳ thực tập Hè năm {self.year}"
        # Ensure only 1 active term at a time
        if self.is_active:
            InternshipTerm.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        """Trả về kỳ thực tập đang active. None nếu chưa có."""
        return cls.objects.filter(is_active=True).first()

    def __str__(self):
        status = " [ĐANG MỞ]" if self.is_active else ""
        return f"{self.name}{status}"


# ==============================================================================
# 2. DEADLINE SYSTEM (per-term, tách riêng weekly / final)
# ==============================================================================

class WeeklyDeadline(models.Model):
    """
    Deadline cho từng tuần, gắn với term (không gắn per-assignment).
    Admin / Lecturer có thể sửa. Ai sửa cuối cùng có hiệu lực.
    Default: Chủ nhật tuần đó.
    """
    term = models.ForeignKey(InternshipTerm, on_delete=models.CASCADE, related_name='weekly_deadlines')
    week_number = models.IntegerField(help_text="1-10")
    title = models.CharField(max_length=255, blank=True, help_text="Tiêu đề bài tập tuần (VD: Cài đặt Linux server)")
    description = models.TextField(blank=True, help_text="Mô tả chi tiết yêu cầu tuần này")
    deadline = models.DateTimeField()
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['term', 'week_number']
        ordering = ['term', 'week_number']
        verbose_name = "Deadline tuần"
        verbose_name_plural = "Deadline tuần"

    def __str__(self):
        return f"Tuần {self.week_number} - {self.term.name} - DL: {self.deadline}"


class FinalDeadline(models.Model):
    """
    Deadline cho báo cáo tổng kết, gắn với term.
    Admin / Lecturer có thể sửa. Ai sửa cuối cùng có hiệu lực.
    """
    term = models.OneToOneField(InternshipTerm, on_delete=models.CASCADE, related_name='final_deadline')
    title = models.CharField(max_length=255, blank=True, default='Báo cáo Tổng kết Thực tập', help_text="Tiêu đề")
    description = models.TextField(blank=True, help_text="Mô tả yêu cầu báo cáo tổng kết")
    deadline = models.DateTimeField()
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Deadline báo cáo tổng kết"
        verbose_name_plural = "Deadline báo cáo tổng kết"

    def __str__(self):
        return f"Final DL - {self.term.name} - {self.deadline}"


# ==============================================================================
# 3. TERM CONFIG
# ==============================================================================

class TermConfig(models.Model):
    """
    Cấu hình cho kỳ thực tập.
    min_required_weeks: số tuần tối thiểu phải nộp trước khi nộp Final.
    """
    term = models.OneToOneField(InternshipTerm, on_delete=models.CASCADE, related_name='config')
    min_required_weeks = models.IntegerField(default=5, help_text="Số tuần tối thiểu cần nộp để nộp Final")

    class Meta:
        verbose_name = "Cấu hình kỳ thực tập"
        verbose_name_plural = "Cấu hình kỳ thực tập"

    def __str__(self):
        return f"Config: {self.term.name} (min_weeks={self.min_required_weeks})"


# ==============================================================================
# 4. MENTOR GROUP
# ==============================================================================

class MentorGroup(models.Model):
    term = models.ForeignKey(InternshipTerm, on_delete=models.CASCADE, related_name='mentor_groups')
    department = models.ForeignKey(DepartmentProfile, on_delete=models.CASCADE, related_name='mentor_groups')
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='mentor_groups')
    name = models.CharField(max_length=200)
    capacity = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ('term', 'department', 'mentor'),
            ('term', 'department', 'name'),
        ]

    def __str__(self):
        return f"{self.name} - {self.mentor} ({self.term.name})"


# ==============================================================================
# 5. INTERNSHIP ASSIGNMENT
# ==============================================================================

class InternshipAssignment(models.Model):
    """
    Kết nối Sinh viên (thông qua Application đã được accepted) với Giảng viên hướng dẫn.
    Giữ các mốc thời gian của riêng đợt thực tập này.
    """
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='assignment', null=True, blank=True)
    external_request = models.OneToOneField('recruitment.ExternalInternshipRequest', on_delete=models.CASCADE, related_name='assignment', null=True, blank=True)
    lecturer = models.ForeignKey(LecturerProfile, on_delete=models.SET_NULL, related_name='assignments', null=True, blank=True)
    term = models.ForeignKey(InternshipTerm, on_delete=models.SET_NULL, related_name='assignments', null=True, blank=True, verbose_name="Kỳ thực tập")
    department = models.ForeignKey(DepartmentProfile, on_delete=models.SET_NULL, related_name='assignments', null=True, blank=True)
    mentor_group = models.ForeignKey(MentorGroup, on_delete=models.SET_NULL, related_name='assignments', null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def get_company_name(self):
        try:
            if self.application and self.application.post and self.application.post.department:
                return str(self.application.post.department)
        except AttributeError:
            pass
        try:
            if self.external_request:
                name = self.external_request.company_name
                if name and name.strip():
                    return name.strip()
        except AttributeError:
            pass
        return "Chưa cập nhật doanh nghiệp"

    @property
    def get_position_name(self):
        try:
            if self.application and self.application.post:
                return self.application.post.title
        except AttributeError:
            pass
        try:
            if self.external_request:
                return self.external_request.position
        except AttributeError:
            pass
        return "Chưa cập nhật vị trí"

    @property
    def get_student(self):
        try:
            if self.application and self.application.student:
                return self.application.student
        except AttributeError:
            pass
        try:
            if self.external_request and self.external_request.student:
                return self.external_request.student
        except AttributeError:
            pass
        return None

    def __str__(self):
        lect_name = self.lecturer.user.username if self.lecturer else "Chưa phân công"
        student_name = self.get_student.user.username if self.get_student else "No Student"
        return f"Assignment: {student_name} - {lect_name}"


# ==============================================================================
# 6. WEEKLY REPORT (pre-created, lock/submit logic)
# ==============================================================================

class WeeklyReport(models.Model):
    """
    Báo cáo hàng tuần do Sinh viên nộp.
    Được tạo sẵn 10 tuần khi Assignment được tạo.
    """
    assignment = models.ForeignKey(InternshipAssignment, on_delete=models.CASCADE, related_name='weekly_reports')
    week_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to='reports/weekly/', null=True, blank=True)

    is_submitted = models.BooleanField(default=False, help_text="SV đã nộp?")
    is_locked = models.BooleanField(default=False, help_text="Đã khóa - không cho nộp lại?")
    is_late = models.BooleanField(default=False, help_text="Nộp trễ?")
    submitted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['week_number']
        unique_together = ['assignment', 'week_number']

    def __str__(self):
        student = self.assignment.get_student
        student_name = student.user.username if student else "Unknown"
        return f"Week {self.week_number} - {student_name}"


# ==============================================================================
# 7. FINAL REPORT (pre-created, lock/submit + min_weeks condition)
# ==============================================================================

class FinalReport(models.Model):
    """
    Báo cáo tổng kết đợt thực tập do Sinh viên nộp.
    Được tạo sẵn khi Assignment được tạo.
    Điều kiện nộp: số tuần is_submitted >= min_required_weeks (TermConfig).
    """
    assignment = models.OneToOneField(InternshipAssignment, on_delete=models.CASCADE, related_name='final_report')
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to='reports/final/', null=True, blank=True)

    is_submitted = models.BooleanField(default=False, help_text="SV đã nộp?")
    is_locked = models.BooleanField(default=False, help_text="Đã khóa - không cho nộp lại?")
    is_late = models.BooleanField(default=False, help_text="Nộp trễ?")
    submitted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        student = self.assignment.get_student
        student_name = student.user.username if student else "Unknown"
        return f"Final Report: {student_name}"


# ==============================================================================
# 8. DEPARTMENT-LECTURER ASSIGNMENT (giữ nguyên)
# ==============================================================================

class DepartmentLecturerAssignment(models.Model):
    """
    Mapping doanh nghiệp (Department) và Giảng viên hướng dẫn (Lecturer).
    Dành cho chức năng tự động gán Giảng viên khi Sinh viên chốt điểm thực tập tại doanh nghiệp này.
    """
    department = models.OneToOneField(DepartmentProfile, on_delete=models.CASCADE, related_name='lecturer_mapping')
    lecturer = models.ForeignKey(LecturerProfile, on_delete=models.CASCADE, related_name='department_mappings')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        lect_name = self.lecturer.user.get_full_name() or self.lecturer.user.username
        comp_name = self.department.organization_name
        return f"{comp_name} => GV: {lect_name}"


# ==============================================================================
# 9. EXTERNAL INTERNSHIP LECTURER CONFIG (giữ nguyên)
# ==============================================================================

class ExternalInternshipLecturerConfig(models.Model):
    """
    Cấu hình Giảng viên phụ trách chung cho Nhóm Thực tập Ngoài.
    Chỉ luưu 1 bản ghi duy nhất. Sử dụng get_solo() để truy cập.
    """
    lecturer = models.ForeignKey(
        LecturerProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='external_internship_config',
        verbose_name="Giảng viên phụ trách Thực tập Ngoài",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cấu hình GV Thực tập Ngoài"

    @classmethod
    def get_solo(cls):
        """Lấy bản ghi cấu hình duy nhất, tạo mới nếu chưa có."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        if self.lecturer:
            return f"GV Thực tập Ngoài: {self.lecturer.user.get_full_name() or self.lecturer.user.username}"
        return "GV Thực tập Ngoài: Chưa cấu hình"


# ==============================================================================
# 10. LECTURER FEEDBACK (giữ nguyên)
# ==============================================================================

class LecturerFeedback(models.Model):
    """
    Nhận xét của giảng viên. Cấu trúc linh hoạt có thể ghim vào Weekly hoặc Final report.
    """
    weekly_report = models.OneToOneField(WeeklyReport, on_delete=models.CASCADE, related_name='feedback', null=True, blank=True)
    final_report = models.OneToOneField(FinalReport, on_delete=models.CASCADE, related_name='feedback', null=True, blank=True)
    feedback_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.weekly_report:
            return f"Feedback for Weekly {self.weekly_report}"
        elif self.final_report:
            return f"Feedback for Final {self.final_report}"
        return "Unlinked Feedback"


# ==============================================================================
# 11. GRADING (giữ nguyên logic)
# ==============================================================================

class WeeklyReportGrade(models.Model):
    GRADER_CHOICES = [
        ('mentor', 'Mentor'),
        ('lecturer', 'Lecturer'),
    ]
    weekly_report = models.ForeignKey(WeeklyReport, on_delete=models.CASCADE, related_name='grades')
    grader_type = models.CharField(max_length=20, choices=GRADER_CHOICES)
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, null=True, blank=True)
    lecturer = models.ForeignKey(LecturerProfile, on_delete=models.CASCADE, null=True, blank=True)
    score = models.DecimalField(max_digits=4, decimal_places=2)
    comment = models.TextField(blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['weekly_report', 'grader_type']

    def clean(self):
        if self.score is not None and (self.score < 0 or self.score > 10):
            raise ValidationError("Score must be between 0 and 10.")
        if self.grader_type == 'mentor':
            if not self.mentor:
                raise ValidationError("Mentor profile is required for mentor grader.")
            if self.lecturer:
                raise ValidationError("Lecturer profile must be empty for mentor grader.")
        elif self.grader_type == 'lecturer':
            if not self.lecturer:
                raise ValidationError("Lecturer profile is required for lecturer grader.")
            if self.mentor:
                raise ValidationError("Mentor profile must be empty for lecturer grader.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.grader_type} grade for {self.weekly_report}"


class FinalReportGrade(models.Model):
    GRADER_CHOICES = [
        ('mentor', 'Mentor'),
        ('lecturer', 'Lecturer'),
    ]
    final_report = models.ForeignKey(FinalReport, on_delete=models.CASCADE, related_name='grades')
    grader_type = models.CharField(max_length=20, choices=GRADER_CHOICES)
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, null=True, blank=True)
    lecturer = models.ForeignKey(LecturerProfile, on_delete=models.CASCADE, null=True, blank=True)
    score = models.DecimalField(max_digits=4, decimal_places=2)
    comment = models.TextField(blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['final_report', 'grader_type']

    def clean(self):
        if self.score is not None and (self.score < 0 or self.score > 10):
            raise ValidationError("Score must be between 0 and 10.")
        if self.grader_type == 'mentor':
            if not self.mentor:
                raise ValidationError("Mentor profile is required for mentor grader.")
            if self.lecturer:
                raise ValidationError("Lecturer profile must be empty for mentor grader.")
        elif self.grader_type == 'lecturer':
            if not self.lecturer:
                raise ValidationError("Lecturer profile is required for lecturer grader.")
            if self.mentor:
                raise ValidationError("Mentor profile must be empty for lecturer grader.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.grader_type} grade for {self.final_report}"


# ==============================================================================
# 12. REPORT COMMENTS (bình luận & phản hồi trên báo cáo)
# ==============================================================================

class ReportComment(models.Model):
    """
    Bình luận trên báo cáo tuần hoặc tổng kết.
    Hỗ trợ thread reply (parent). GV, SV, Mentor đều có thể bình luận.
    """
    weekly_report = models.ForeignKey(
        WeeklyReport, on_delete=models.CASCADE,
        related_name='comments', null=True, blank=True,
    )
    final_report = models.ForeignKey(
        FinalReport, on_delete=models.CASCADE,
        related_name='comments', null=True, blank=True,
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_comments')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='replies',
    )
    content = models.TextField(help_text="Nội dung bình luận")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Bình luận báo cáo"
        verbose_name_plural = "Bình luận báo cáo"

    def __str__(self):
        target = self.weekly_report or self.final_report
        return f"Comment by {self.author.username} on {target}"
