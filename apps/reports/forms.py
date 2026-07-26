from django import forms

from .models import (
    WeeklyReport, FinalReport, LecturerFeedback,
    DepartmentLecturerAssignment, InternshipTerm, InternshipAssignment,
    ExternalInternshipLecturerConfig, TermConfig,
)


class WeeklyReportForm(forms.ModelForm):
    """Form cho SV điền nội dung báo cáo tuần (report đã tạo sẵn)."""
    class Meta:
        model = WeeklyReport
        fields = ['title', 'content', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Báo cáo công việc tuần 1...'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Tóm tắt các công việc đã thực hiện...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Tiêu đề báo cáo',
            'content': 'Nội dung thực hiện',
            'attachment': 'Đính kèm tệp (PDF/DOCX)',
        }


class FinalReportForm(forms.ModelForm):
    class Meta:
        model = FinalReport
        fields = ['title', 'content', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Báo cáo kết quả thực tập tổng hợp...'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Tiêu đề báo cáo',
            'content': 'Tổng kết toàn bộ quá trình (hoặc lưu ý thêm)',
            'attachment': 'Đính kèm bản báo cáo chi tiết (Bắt buộc)',
        }


class LecturerFeedbackForm(forms.ModelForm):
    class Meta:
        model = LecturerFeedback
        fields = ['feedback_content']
        widgets = {
            'feedback_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Nhập nhận xét / góp ý cho báo cáo này...'}),
        }
        labels = {
            'feedback_content': 'Nội dung nhận xét',
        }


class MentorGradeForm(forms.Form):
    score = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.25',
            'placeholder': '0.00 - 10.00'
        }),
        label='Điểm Mentor'
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Nhập nhận xét của Mentor...'
        }),
        label='Nhận xét Mentor'
    )


class LecturerGradeForm(forms.Form):
    score = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.25',
            'placeholder': '0.00 - 10.00'
        }),
        label='Điểm Giảng viên'
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Nhập nhận xét của Giảng viên...'
        }),
        label='Nhận xét Giảng viên'
    )


class FinalReportMentorGradeForm(forms.Form):
    score = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.25',
            'placeholder': '0.00 - 10.00'
        }),
        label='Điểm Mentor'
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Nhập nhận xét của Mentor...'
        }),
        label='Nhận xét Mentor'
    )


class FinalReportLecturerGradeForm(forms.Form):
    score = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.25',
            'placeholder': '0.00 - 10.00'
        }),
        label='Điểm Giảng viên'
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Nhập nhận xét của Giảng viên...'
        }),
        label='Nhận xét Giảng viên'
    )


class DepartmentLecturerAssignmentForm(forms.ModelForm):
    class Meta:
        model = DepartmentLecturerAssignment
        fields = ['department', 'lecturer']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'lecturer': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'department': 'Doanh nghiệp tiếp nhận',
            'lecturer': 'Giảng viên phụ trách',
        }


class InternshipTermForm(forms.ModelForm):
    """Form cho tạo/sửa kỳ thực tập. Name auto-generated từ year."""
    class Meta:
        model = InternshipTerm
        fields = ['year', 'start_date', 'end_date', 'is_active']
        widgets = {
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VD: 2026'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'year': 'Năm thực tập',
            'start_date': 'Ngày Bắt đầu',
            'end_date': 'Ngày Kết thúc',
            'is_active': 'Kích hoạt làm Kỳ Hiện tại (Tự thay thế các kỳ cũ)',
        }


class InternshipAssignmentForm(forms.ModelForm):
    class Meta:
        model = InternshipAssignment
        fields = ['lecturer', 'start_date', 'end_date', 'is_active']
        widgets = {
            'lecturer': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'lecturer': 'Giảng viên Hướng dẫn',
            'start_date': 'Ngày Bắt đầu',
            'end_date': 'Ngày Kết thúc',
            'is_active': 'Trạng thái Hoạt động (Cho phép SV nộp báo cáo)',
        }


class ExternalInternshipLecturerConfigForm(forms.ModelForm):
    class Meta:
        model = ExternalInternshipLecturerConfig
        fields = ['lecturer']
        widgets = {
            'lecturer': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'lecturer': 'Giảng viên phụ trách Nhóm Thực tập Ngoài',
        }


class TermConfigForm(forms.ModelForm):
    """Form cho cấu hình kỳ thực tập."""
    class Meta:
        model = TermConfig
        fields = ['min_required_weeks']
        widgets = {
            'min_required_weeks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }
        labels = {
            'min_required_weeks': 'Số tuần tối thiểu cần nộp để nộp Final',
        }


from .models import WeeklyDeadline, FinalDeadline


class WeeklyDeadlineForm(forms.ModelForm):
    """Form cho GV chỉnh tiêu đề, mô tả yêu cầu và deadline từng tuần."""
    class Meta:
        model = WeeklyDeadline
        fields = ['title', 'description', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Cài đặt Linux server và các dịch vụ'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Mô tả chi tiết yêu cầu tuần này...'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        labels = {
            'title': 'Tiêu đề bài tập',
            'description': 'Yêu cầu chi tiết',
            'deadline': 'Hạn nộp',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.deadline:
            self.initial['deadline'] = self.instance.deadline.strftime('%Y-%m-%dT%H:%M')


class FinalDeadlineForm(forms.ModelForm):
    """Form cho GV chỉnh tiêu đề, mô tả và deadline báo cáo tổng kết."""
    class Meta:
        model = FinalDeadline
        fields = ['title', 'description', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Mô tả yêu cầu báo cáo tổng kết...'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        labels = {
            'title': 'Tiêu đề',
            'description': 'Yêu cầu chi tiết',
            'deadline': 'Hạn nộp',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.deadline:
            self.initial['deadline'] = self.instance.deadline.strftime('%Y-%m-%dT%H:%M')


from .models import ReportComment


class ReportCommentForm(forms.ModelForm):
    """Form cho bình luận trên báo cáo."""
    class Meta:
        model = ReportComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Nhập bình luận...',
            }),
        }
        labels = {
            'content': 'Nội dung bình luận',
        }

