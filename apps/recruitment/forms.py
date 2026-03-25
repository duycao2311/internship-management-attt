from django import forms
from .models import InternshipPost, CV, Application, ExternalInternshipRequest

class InternshipPostForm(forms.ModelForm):
    class Meta:
        model = InternshipPost
        fields = ['title', 'description', 'requirements', 'deadline', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class CVUploadForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: CV Tiếng Việt'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cv']
        widgets = {
            'cv': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        student_profile = kwargs.pop('student_profile', None)
        super(ApplicationForm, self).__init__(*args, **kwargs)
        if student_profile:
            self.fields['cv'].queryset = CV.objects.filter(student=student_profile)
            self.fields['cv'].empty_label = "--- Chọn CV của bạn ---"

class ExternalInternshipRequestForm(forms.ModelForm):
    class Meta:
        model = ExternalInternshipRequest
        fields = ['company_name', 'position', 'contact_person', 'contact_email', 'contact_phone', 'address', 'start_date', 'end_date', 'note']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: CÔNG TY TNHH ABC'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Thực tập sinh Backend'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Nguyễn Văn A'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: hr@abc.com'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: 0987xxx'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ghi chú thêm...'}),
        }
