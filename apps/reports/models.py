from django.db import models
from apps.accounts.models import LecturerProfile, DepartmentProfile
from apps.recruitment.models import Application

class InternshipPeriod(models.Model):
    name = models.CharField(max_length=255, help_text="VD: Học kỳ 1 Năm học 2024-2025")
    start_date = models.DateField(help_text="Ngày bắt đầu thực tập")
    end_date = models.DateField(help_text="Ngày kết thúc thực tập")
    is_active = models.BooleanField(default=False, help_text="Chỉ định 1 kỳ được mở tại một thời điểm")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = " [ĐANG MỞ]" if self.is_active else ""
        return f"{self.name}{status}"
    
    def save(self, *args, **kwargs):
        if self.is_active:
            InternshipPeriod.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

class InternshipAssignment(models.Model):
    """
    Kết nối Sinh viên (thông qua Application đã được accepted) với Giảng viên hướng dẫn.
    Giữ các mốc thời gian của riêng đợt thực tập này.
    """
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='assignment', null=True, blank=True)
    external_request = models.OneToOneField('recruitment.ExternalInternshipRequest', on_delete=models.CASCADE, related_name='assignment', null=True, blank=True)
    lecturer = models.ForeignKey(LecturerProfile, on_delete=models.SET_NULL, related_name='assignments', null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def get_company_name(self):
        if self.application:
            return self.application.post.department.organization_name
        if self.external_request:
            return self.external_request.company_name
        return "Chưa rõ"

    @property
    def get_position_name(self):
        if self.application:
            return self.application.post.title
        if self.external_request:
            return self.external_request.position
        return "Chưa rõ"

    @property
    def get_student(self):
        if self.application:
            return self.application.student
        if self.external_request:
            return self.external_request.student
        return None

    def __str__(self):
        lect_name = self.lecturer.user.username if self.lecturer else "Chưa phân công"
        student_name = self.get_student.user.username if self.get_student else "No Student"
        return f"Assignment: {student_name} - {lect_name}"


class WeeklyReport(models.Model):
    """
    Báo cáo hàng tuần do Sinh viên nộp.
    """
    STATUS_CHOICES = [
        ('draft', 'Bản nháp'),
        ('submitted', 'Đã nộp'),
    ]
    assignment = models.ForeignKey(InternshipAssignment, on_delete=models.CASCADE, related_name='weekly_reports')
    week_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    attachment = models.FileField(upload_to='reports/weekly/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-week_number']
        unique_together = ['assignment', 'week_number']

    def __str__(self):
        student = self.assignment.get_student
        student_name = student.user.username if student else "Unknown"
        return f"Week {self.week_number} - {student_name}"


class FinalReport(models.Model):
    """
    Báo cáo tổng kết đợt thực tập do Sinh viên nộp.
    """
    assignment = models.OneToOneField(InternshipAssignment, on_delete=models.CASCADE, related_name='final_report')
    title = models.CharField(max_length=200)
    content = models.TextField()
    attachment = models.FileField(upload_to='reports/final/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        student = self.assignment.get_student
        student_name = student.user.username if student else "Unknown"
        return f"Final Report: {student_name}"


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
