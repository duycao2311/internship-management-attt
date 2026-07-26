"""
Seed script tạo data mẫu cho hệ thống thực tập.
Chạy: python manage.py shell < seed_data.py
Hoặc: python manage.py shell -c "exec(open('seed_data.py').read())"
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stellar_core.settings')
django.setup()

from django.utils import timezone
from datetime import date, timedelta
from apps.accounts.models import User, StudentProfile, DepartmentProfile, LecturerProfile, MentorProfile
from apps.recruitment.models import InternshipPost, CV, Application, ExternalInternshipRequest
from apps.reports.models import (
    InternshipTerm, WeeklyDeadline, FinalDeadline, TermConfig,
    DepartmentLecturerAssignment, MentorGroup, InternshipAssignment,
)
from apps.reports.services.term_service import create_default_term, set_active_term
from apps.reports.services.deadline_service import generate_weekly_deadlines

DEFAULT_PW = 'thuctapattt@'

print("=" * 60)
print("  SEED DATA - Hệ thống Quản lý Thực tập ATTT - PTIT")
print("=" * 60)

# ===== 1. SUPERUSER =====
print("\n[1/9] Tạo SuperUser...")
su, created = User.objects.get_or_create(username='buivancong', defaults={
    'role': 'admin', 'is_staff': True, 'is_superuser': True,
    'first_name': 'Công', 'last_name': 'Bùi Văn',
    'email': 'buivancong@ptit.edu.vn',
})
su.set_password(DEFAULT_PW)
su.save()
print(f"  {'Đã tạo' if created else 'Đã tồn tại'}: buivancong (superuser)")

# ===== 2. ADMIN =====
print("\n[2/9] Tạo Admin...")
admin1, c = User.objects.get_or_create(username='admin1', defaults={
    'role': 'admin', 'is_staff': True,
    'first_name': 'Quản trị', 'last_name': 'Admin',
})
admin1.set_password(DEFAULT_PW)
admin1.save()
print(f"  {'Đã tạo' if c else 'Đã tồn tại'}: admin1")

# ===== 3. DEPARTMENTS (Doanh nghiệp) =====
print("\n[3/9] Tạo Doanh nghiệp...")
depts_data = [
    {'username': 'VNPT', 'org': 'Tập đoàn VNPT', 'contact': 'Nguyễn Văn A', 'email': 'hr@vnpt.vn', 'phone': '0243-1234567', 'addr': 'Hà Nội'},
    {'username': 'FPT', 'org': 'FPT Software', 'contact': 'Trần Thị B', 'email': 'hr@fpt.vn', 'phone': '0243-7654321', 'addr': 'Cầu Giấy, Hà Nội'},
    {'username': 'department1', 'org': 'Viettel Cyber Security', 'contact': 'Lê Văn C', 'email': 'hr@viettel.vn', 'phone': '0243-9876543', 'addr': 'Hà Nội'},
    {'username': 'department2', 'org': 'CMC Telecom', 'contact': 'Phạm Thị D', 'email': 'hr@cmc.vn', 'phone': '0243-1112233', 'addr': 'Hà Nội'},
]
dept_profiles = {}
for d in depts_data:
    user, c = User.objects.get_or_create(username=d['username'], defaults={'role': 'department'})
    user.set_password(DEFAULT_PW)
    user.save()
    profile, _ = DepartmentProfile.objects.get_or_create(user=user, defaults={
        'organization_name': d['org'], 'contact_person': d['contact'],
        'email': d['email'], 'phone': d['phone'], 'address': d['addr'],
        'description': f"Đơn vị {d['org']} tuyển dụng thực tập sinh ATTT.",
    })
    dept_profiles[d['username']] = profile
    print(f"  {'Tạo' if c else 'OK'}: {d['username']} → {d['org']}")

# ===== 4. LECTURERS (Giảng viên) =====
print("\n[4/9] Tạo Giảng viên...")
lect_data = [
    {'username': 'lecturer1', 'full': 'Nguyễn Văn Giảng', 'faculty': 'Khoa ATTT', 'spec': 'An toàn mạng'},
    {'username': 'lecturer2', 'full': 'Trần Thị Hương', 'faculty': 'Khoa ATTT', 'spec': 'Mật mã học'},
]
lect_profiles = {}
for l in lect_data:
    user, c = User.objects.get_or_create(username=l['username'], defaults={
        'role': 'lecturer', 'first_name': l['full'].split()[-1], 'last_name': ' '.join(l['full'].split()[:-1]),
    })
    user.set_password(DEFAULT_PW)
    user.save()
    profile, _ = LecturerProfile.objects.get_or_create(user=user, defaults={
        'full_name': l['full'], 'faculty': l['faculty'], 'phone': '0912345678', 'specialization': l['spec'],
    })
    lect_profiles[l['username']] = profile
    print(f"  {'Tạo' if c else 'OK'}: {l['username']} → {l['full']}")

# buivancong cũng là lecturer
bvc_user = User.objects.get(username='buivancong')
bvc_lect, _ = LecturerProfile.objects.get_or_create(user=bvc_user, defaults={
    'full_name': 'Bùi Văn Công', 'faculty': 'Khoa ATTT', 'phone': '0987654321', 'specialization': 'An ninh mạng',
})
lect_profiles['buivancong'] = bvc_lect
print(f"  OK: buivancong → Bùi Văn Công (lecturer)")

# ===== 5. MENTORS =====
print("\n[5/9] Tạo Mentor...")
mentor_data = [
    {'username': 'vnpt_mentor_1', 'full': 'Hoàng Minh Tuấn', 'dept': 'VNPT', 'title': 'Senior Engineer'},
    {'username': 'fpt_mentor_1', 'full': 'Đỗ Thanh Hải', 'dept': 'FPT', 'title': 'Tech Lead'},
]
mentor_profiles = {}
for m in mentor_data:
    user, c = User.objects.get_or_create(username=m['username'], defaults={
        'role': 'mentor', 'first_name': m['full'].split()[-1], 'last_name': ' '.join(m['full'].split()[:-1]),
    })
    user.set_password(DEFAULT_PW)
    user.save()
    profile, _ = MentorProfile.objects.get_or_create(user=user, defaults={
        'full_name': m['full'], 'department': dept_profiles[m['dept']],
        'phone': '0901234567', 'job_title': m['title'],
    })
    mentor_profiles[m['username']] = profile
    print(f"  {'Tạo' if c else 'OK'}: {m['username']} → {m['full']} ({m['dept']})")

# ===== 6. STUDENTS (Sinh viên) =====
print("\n[6/9] Tạo Sinh viên...")
students_data = [
    {'username': 'B23DCAT076', 'fn': 'Phước', 'ln': 'Duy Cao', 'cls': 'D23CQAT02-B', 'sid': 'B23DCAT076'},
    {'username': 'B23DCAT042', 'fn': 'Hoàng', 'ln': 'Nguyễn Văn', 'cls': 'D23CQAT01-B', 'sid': 'B23DCAT042'},
    {'username': 'B23DCAT032', 'fn': 'Đức', 'ln': 'Trần Văn', 'cls': 'D23CQAT01-B', 'sid': 'B23DCAT032'},
    {'username': 'B23DCAT021', 'fn': 'Bình', 'ln': 'Lê Văn', 'cls': 'D23CQAT02-B', 'sid': 'B23DCAT021'},
    {'username': 'B23DCAT004', 'fn': 'An', 'ln': 'Phạm Văn', 'cls': 'D23CQAT01-B', 'sid': 'B23DCAT004'},
    {'username': 'student1', 'fn': 'Minh', 'ln': 'Nguyễn', 'cls': 'D23CQAT02-B', 'sid': 'S001'},
    {'username': 'student2', 'fn': 'Hùng', 'ln': 'Trần', 'cls': 'D23CQAT01-B', 'sid': 'S002'},
    {'username': 'student3', 'fn': 'Linh', 'ln': 'Phạm Thị', 'cls': 'D23CQAT02-B', 'sid': 'S003'},
    {'username': 'student4', 'fn': 'Tùng', 'ln': 'Đỗ Văn', 'cls': 'D23CQAT01-B', 'sid': 'S004'},
]
student_profiles = {}
for s in students_data:
    user, c = User.objects.get_or_create(username=s['username'], defaults={
        'role': 'student', 'first_name': s['fn'], 'last_name': s['ln'],
    })
    user.set_password(DEFAULT_PW)
    user.save()
    profile, _ = StudentProfile.objects.get_or_create(user=user, defaults={
        'student_id': s['sid'], 'class_name': s['cls'], 'major': 'An toàn thông tin', 'phone': '0900000000',
    })
    student_profiles[s['username']] = profile
    print(f"  {'Tạo' if c else 'OK'}: {s['username']} → {s['ln']} {s['fn']}")

# ===== 7. INTERNSHIP TERM + DEADLINES =====
print("\n[7/9] Tạo Kỳ thực tập 2026 + Deadlines...")
term = create_default_term(2026)
set_active_term(term)
generate_weekly_deadlines(term)
TermConfig.objects.get_or_create(term=term, defaults={'min_required_weeks': 5})
print(f"  Term: {term.name} ({term.start_date} → {term.end_date}) [ACTIVE]")
print(f"  Weekly deadlines: {WeeklyDeadline.objects.filter(term=term).count()}")
print(f"  Final deadline: {FinalDeadline.objects.filter(term=term).count()}")

# ===== 8. DEPARTMENT-LECTURER MAPPING + MENTOR GROUPS =====
print("\n[8/9] Tạo phân công GV-DN + Mentor Groups...")
DepartmentLecturerAssignment.objects.get_or_create(department=dept_profiles['VNPT'], defaults={'lecturer': lect_profiles['lecturer1']})
DepartmentLecturerAssignment.objects.get_or_create(department=dept_profiles['FPT'], defaults={'lecturer': lect_profiles['lecturer2']})
DepartmentLecturerAssignment.objects.get_or_create(department=dept_profiles['department1'], defaults={'lecturer': lect_profiles['buivancong']})
print("  Phân công: VNPT→lecturer1, FPT→lecturer2, Viettel→buivancong")

mg_vnpt, _ = MentorGroup.objects.get_or_create(
    term=term, department=dept_profiles['VNPT'], mentor=mentor_profiles['vnpt_mentor_1'],
    defaults={'name': 'Nhóm VNPT - Hoàng Minh Tuấn', 'capacity': 10},
)
mg_fpt, _ = MentorGroup.objects.get_or_create(
    term=term, department=dept_profiles['FPT'], mentor=mentor_profiles['fpt_mentor_1'],
    defaults={'name': 'Nhóm FPT - Đỗ Thanh Hải', 'capacity': 10},
)
print(f"  Mentor Groups: {mg_vnpt.name}, {mg_fpt.name}")

# ===== 9. POSTS + APPLICATIONS + ASSIGNMENTS =====
print("\n[9/9] Tạo tin tuyển dụng, ứng tuyển, assignment...")

# Tạo tin tuyển dụng
post_vnpt, _ = InternshipPost.objects.get_or_create(
    department=dept_profiles['VNPT'], title='Thực tập sinh An ninh mạng',
    defaults={'description': 'Tham gia đội SOC, phân tích log, phát hiện xâm nhập.',
              'requirements': 'Kiến thức TCP/IP, Linux, biết dùng Wireshark.',
              'status': 'open', 'deadline': date(2026, 6, 15)},
)
post_fpt, _ = InternshipPost.objects.get_or_create(
    department=dept_profiles['FPT'], title='Thực tập sinh Pentest',
    defaults={'description': 'Thực hiện kiểm thử xâm nhập cho khách hàng doanh nghiệp.',
              'requirements': 'Biết dùng Burp Suite, Nmap, OWASP Top 10.',
              'status': 'open', 'deadline': date(2026, 6, 15)},
)
print(f"  Posts: {post_vnpt.title}, {post_fpt.title}")

# Tạo application + assignment cho 6 sinh viên
assignments_map = [
    # (student_key, post, lecturer_key, mentor_group)
    ('B23DCAT076', post_vnpt, 'lecturer1', mg_vnpt),
    ('B23DCAT042', post_vnpt, 'lecturer1', mg_vnpt),
    ('B23DCAT032', post_fpt, 'lecturer2', mg_fpt),
    ('B23DCAT021', post_fpt, 'lecturer2', mg_fpt),
    ('student1', post_vnpt, 'lecturer1', mg_vnpt),
    ('student2', post_fpt, 'lecturer2', mg_fpt),
]

from apps.reports.models import WeeklyReport, FinalReport

for sk, post, lk, mg in assignments_map:
    sp = student_profiles[sk]
    app, _ = Application.objects.get_or_create(
        post=post, student=sp,
        defaults={'status': 'accepted'},
    )
    assignment, created_a = InternshipAssignment.objects.get_or_create(
        application=app,
        defaults={
            'lecturer': lect_profiles[lk], 'term': term,
            'department': post.department, 'mentor_group': mg,
            'start_date': term.start_date, 'end_date': term.end_date,
            'is_active': True,
        },
    )
    if created_a:
        # Signal tự tạo 10 weekly + 1 final, nhưng nếu signal chưa chạy thì tạo thủ công
        if not WeeklyReport.objects.filter(assignment=assignment).exists():
            for wn in range(1, 11):
                WeeklyReport.objects.create(assignment=assignment, week_number=wn)
        if not FinalReport.objects.filter(assignment=assignment).exists():
            FinalReport.objects.create(assignment=assignment)

    print(f"  {sk} → {post.department.organization_name} (GV: {lk}, MG: {mg.name})")

# Giả lập một số sinh viên đã nộp bài tuần 1-3
print("\n  Giả lập nộp bài tuần 1-3 cho B23DCAT076, B23DCAT042...")
for sk in ['B23DCAT076', 'B23DCAT042']:
    sp = student_profiles[sk]
    assignment = InternshipAssignment.objects.filter(application__student=sp).first()
    if assignment:
        for wn in range(1, 4):
            report = WeeklyReport.objects.filter(assignment=assignment, week_number=wn).first()
            if report and not report.is_submitted:
                report.title = f'Báo cáo tuần {wn}'
                report.content = f'Nội dung báo cáo tuần {wn}: Hoàn thành các task được giao, tìm hiểu hệ thống.'
                report.is_submitted = True
                report.is_locked = True
                report.submitted_at = timezone.now() - timedelta(weeks=3-wn)
                report.save()

print("\n" + "=" * 60)
print("  SEED HOÀN TẤT!")
print("=" * 60)
print(f"""
Tổng kết:
  - SuperUser: buivancong / {DEFAULT_PW}
  - Admin: admin1 / {DEFAULT_PW}
  - Sinh viên: B23DCAT076, B23DCAT042, B23DCAT032, B23DCAT021, student1-4
  - Doanh nghiệp: VNPT, FPT, department1, department2
  - Giảng viên: lecturer1, lecturer2, buivancong
  - Mentor: vnpt_mentor_1, fpt_mentor_1
  - Kỳ thực tập: {term.name} [ACTIVE]
  - 6 assignments với 10 weekly + 1 final đã pre-generate
  - 2 SV đã nộp tuần 1-3

Mật khẩu tất cả: {DEFAULT_PW}
""")
