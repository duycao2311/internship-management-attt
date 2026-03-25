from django import forms
from .models import WeeklyReport, FinalReport, LecturerFeedback, DepartmentLecturerAssignment, InternshipPeriod, InternshipAssignment

class WeeklyReportForm(forms.ModelForm):
    class Meta:
        model = WeeklyReport
        fields = ['week_number', 'title', 'content', 'attachment', 'status']
        widgets = {
            'week_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Báo cáo công việc tuần 1...'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Tóm tắt các công việc đã thực hiện...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'week_number': 'Tuần số',
            'title': 'Tiêu đề báo cáo',
            'content': 'Nội dung thực hiện',
            'attachment': 'Đính kèm tệp (PDF/DOCX)',
            'status': 'Trạng thái lưu',
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

class InternshipPeriodForm(forms.ModelForm):
    class Meta:
        model = InternshipPeriod
        fields = ['name', 'start_date', 'end_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Kỳ Thực tập Hè 2025'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'name': 'Tên Kỳ thực tập',
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
