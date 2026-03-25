from django.db import models
from apps.accounts.models import DepartmentProfile, StudentProfile

class InternshipPost(models.Model):
    STATUS_CHOICES = [
        ('open', 'Mở đăng ký'),
        ('closed', 'Đóng đăng ký'),
    ]
    department = models.ForeignKey(DepartmentProfile, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200, verbose_name="Tiêu đề")
    description = models.TextField(verbose_name="Mô tả công việc")
    requirements = models.TextField(verbose_name="Yêu cầu")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="Trạng thái")
    deadline = models.DateField(verbose_name="Hạn nộp hồ sơ", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_active(self):
        from django.utils import timezone
        if self.status != 'open':
            return False
        if self.deadline and self.deadline < timezone.now().date():
            return False
        return True

    def __str__(self):
        return f"{self.title} - {self.department.organization_name}"

class CV(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='cvs')
    title = models.CharField(max_length=100, verbose_name="Tên gợi nhớ (VD: CV Backend Python)", default="My CV")
    file = models.FileField(upload_to='cvs/', verbose_name="File CV")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.student.user.username}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Đang chờ duyệt'),
        ('accepted', 'Trúng tuyển'),
        ('rejected', 'Không đạt'),
    ]
    post = models.ForeignKey(InternshipPost, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    cv = models.ForeignKey(CV, on_delete=models.SET_NULL, null=True, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'student') # Một sinh viên chỉ ứng tuyển 1 job 1 lần

    def __str__(self):
        return f"{self.student.user.username} -> {self.post.title}"

class ExternalInternshipRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ phê duyệt'),
        ('approved', 'Đã phê duyệt'),
        ('rejected', 'Đã từ chối'),
    ]
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='external_requests')
    company_name = models.CharField(max_length=255, verbose_name="Tên Doanh nghiệp")
    position = models.CharField(max_length=255, verbose_name="Vị trí thực tập")
    contact_person = models.CharField(max_length=255, verbose_name="Người liên hệ")
    contact_email = models.EmailField(verbose_name="Email người liên hệ")
    contact_phone = models.CharField(max_length=50, blank=True, verbose_name="Số điện thoại")
    address = models.TextField(verbose_name="Địa chỉ Doanh nghiệp")
    
    start_date = models.DateField(verbose_name="Ngày bắt đầu (Dự kiến)")
    end_date = models.DateField(null=True, blank=True, verbose_name="Ngày kết thúc")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    note = models.TextField(blank=True, verbose_name="Ghi chú thêm")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.user.username} -> {self.company_name}"
