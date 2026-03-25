from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import StudentProfile, DepartmentProfile, LecturerProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Tự động tạo profile (StudentProfile, DepartmentProfile, LecturerProfile) cho những User cũ bị thiếu'

    def handle(self, *args, **options):
        users = User.objects.all()
        created_count = 0
        
        self.stdout.write("Bắt đầu rà soát và tạo profile còn thiếu...")
        
        for user in users:
            try:
                if user.role == User.STUDENT:
                    obj, created = StudentProfile.objects.get_or_create(user=user)
                    if created: created_count += 1
                elif user.role == User.DEPARTMENT:
                    obj, created = DepartmentProfile.objects.get_or_create(user=user)
                    if created: created_count += 1
                elif user.role == User.LECTURER:
                    obj, created = LecturerProfile.objects.get_or_create(user=user)
                    if created: created_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Lỗi khi xử lý user {user.username}: {e}"))
                
        self.stdout.write(self.style.SUCCESS(f'Hoàn tất! Đã khởi tạo thành công {created_count} profiles mới.'))
