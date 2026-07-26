"""
Management command: import_students_from_excel
Usage:
  python manage.py import_students_from_excel students.xlsx
  python manage.py import_students_from_excel students.xlsx --only-attt
"""
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Import danh sach sinh vien tu file Excel (.xlsx)"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="Duong dan den file Excel (.xlsx)",
        )
        parser.add_argument(
            "--only-attt",
            action="store_true",
            default=False,
            help="Chi import sinh vien co 'AT' trong ma SV hoac ma lop (khoa ATTT)",
        )

    def handle(self, *args, **options):
        try:
            import openpyxl
        except ImportError:
            raise CommandError(
                "Thu vien 'openpyxl' chua duoc cai dat. Hay chay: pip install openpyxl"
            )

        from apps.accounts.student_import_utils import import_students_from_workbook

        file_path = options["file_path"]
        only_attt = options["only_attt"]

        try:
            wb = openpyxl.load_workbook(file_path, read_only=False, data_only=True)
        except FileNotFoundError:
            raise CommandError(f"Khong tim thay file: {file_path}")
        except Exception as e:
            raise CommandError(f"Loi khi mo file Excel: {e}")

        if only_attt:
            self.stdout.write(self.style.WARNING("Che do: Chi import sinh vien khoa ATTT (loc theo 'AT' trong ma SV / ma lop)."))

        result = import_students_from_workbook(wb, only_attt=only_attt)
        wb.close()

        # In log tung dong
        for line in result["log"]:
            self.stdout.write(f"  {line}")

        # In loi neu co
        for err in result["errors"]:
            self.stdout.write(self.style.ERROR(f"  LOI: {err}"))

        # Tong ket
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 55))
        self.stdout.write(self.style.SUCCESS("TONG KET IMPORT SINH VIEN"))
        self.stdout.write(self.style.SUCCESS("=" * 55))
        self.stdout.write(f"  Tong so dong doc duoc       : {result['total']}")
        if only_attt:
            self.stdout.write(f"  Bo qua (khong phai ATTT)    : {result['skipped_not_attt']}")
        self.stdout.write(f"  User duoc tao moi           : {result['users_created']}")
        self.stdout.write(f"  User duoc cap nhat          : {result['users_updated']}")
        self.stdout.write(f"  Profile duoc tao moi        : {result['profiles_created']}")
        self.stdout.write(f"  Profile duoc cap nhat       : {result['profiles_updated']}")
        self.stdout.write(f"  Dong bi loi                 : {result['failed']}")
        self.stdout.write(self.style.SUCCESS("=" * 55))
