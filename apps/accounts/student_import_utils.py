"""
student_import_utils.py
Logic import sinh vien dung chung giua management command va admin web view.

Ho tro cac format:
  Format A: STT | Ma SV | Ho | Ten | Lop           (cot tach san)
  Format B: Ma SV | Ho va ten | ... | Lop           (1 cot thuc su)
  Format C: Ma SV | [Ho va ten merged 2 cot] | ...  (header gop, data 2 cot)
  Format D: 2 dong header (dong 1 merged, dong 2 sub-headers)
"""
from apps.accounts.models import User, StudentProfile

DEFAULT_PASSWORD = "thuctapattt@"

COLUMN_ALIASES = {
    "masv":     ["masv", "ma sv", "mã sv", "mssv", "mã sinh viên", "ma sinh vien"],
    "ho_dem":   ["ho dem", "họ đệm", "họ", "ho", "last name"],
    "ten":      ["ten", "tên", "first name"],
    "ho_ten":   ["ho ten", "họ tên", "họ và tên", "ho va ten", "hovaten", "ho và tên"],
    "lop":      ["lop", "lớp", "class", "mã lớp", "ma lop"],
}


def _normalize(text: str) -> str:
    if text is None:
        return ""
    return str(text).strip().lower()


def _detect_merged_header(ws, header_row: int = 1) -> dict:
    """
    Kiem tra merged cells trong dong header.
    Tra ve dict {col_start_index: (col_end_index, value)} cho cac merge range.
    Index 0-based.
    """
    merged_info = {}
    if not hasattr(ws, 'merged_cells'):
        return merged_info
    for merge_range in ws.merged_cells.ranges:
        if merge_range.min_row <= header_row <= merge_range.max_row:
            # Merged cell value luon nam o cell goc (min_row, min_col)
            value = ws.cell(row=merge_range.min_row, column=merge_range.min_col).value
            col_start = merge_range.min_col - 1  # 0-based
            col_end = merge_range.max_col - 1     # 0-based
            col_span = col_end - col_start + 1
            merged_info[col_start] = {
                "col_end": col_end,
                "col_span": col_span,
                "value": _normalize(value) if value else "",
            }
    return merged_info


def _is_ho_ten_header(text: str) -> bool:
    """Kiem tra 1 header text co phai la 'Ho va ten' khong."""
    norm = _normalize(text)
    return norm in COLUMN_ALIASES["ho_ten"]


def detect_columns_smart(ws) -> tuple:
    """
    Phat hien cot thong minh, xu ly ca merge header va 2-dong header.

    Tra ve (col_map: dict, data_start_row: int, mode: str)
    mode la 1 trong: 'split_cols', 'merged_2col', 'single_hoten'
    """
    merged_info = _detect_merged_header(ws, header_row=1)

    # Doc header dong 1 (khong dung values_only de giu thong tin merge)
    row1_cells = []
    for col_idx in range(1, ws.max_column + 1):
        val = ws.cell(row=1, column=col_idx).value
        row1_cells.append(_normalize(val) if val else "")

    # Kiem tra xem dong 2 co phai sub-header khong (VD: "Ho" | "Ten")
    row2_cells = []
    has_sub_header = False
    if ws.max_row >= 2:
        for col_idx in range(1, ws.max_column + 1):
            val = ws.cell(row=2, column=col_idx).value
            row2_cells.append(_normalize(val) if val else "")
        # Neu dong 2 co cac tu khoa header thi no la sub-header
        row2_text = " ".join(row2_cells)
        header_keywords = ["họ", "ho", "tên", "ten", "lớp", "lop", "mã sv", "masv"]
        if any(kw in row2_text for kw in header_keywords):
            has_sub_header = True

    # === TH1: Header gop "Ho va ten" merged 2 cot (Format C) ===
    for col_start, info in merged_info.items():
        if _is_ho_ten_header(info["value"]) and info["col_span"] == 2:
            # Merged 2 cot: col_start = ho_dem, col_start+1 = ten
            col_map = {"ho_dem": col_start, "ten": col_start + 1}

            # Tim cac cot khac tu dong 1 (bo qua vung merge)
            merge_cols = set(range(col_start, info["col_end"] + 1))
            for i, h in enumerate(row1_cells):
                if i in merge_cols:
                    continue
                for key, aliases in COLUMN_ALIASES.items():
                    if key in ("ho_ten", "ho_dem", "ten"):
                        continue
                    if h in aliases and key not in col_map:
                        col_map[key] = i

            data_start = 2 if not has_sub_header else 3
            return col_map, data_start, "merged_2col"

    # === TH2: 2 dong header, dong 2 co sub-header (Format D) ===
    if has_sub_header:
        # Uu tien dung dong 2 de detect cot
        col_map = {}
        for key, aliases in COLUMN_ALIASES.items():
            if key == "ho_ten":
                continue
            for i, h in enumerate(row2_cells):
                if h in aliases and key not in col_map:
                    col_map[key] = i
                    break
        if "ten" in col_map or "ho_dem" in col_map:
            return col_map, 3, "split_cols"

    # === TH3: Header binh thuong, 1 dong (Format A hoac B) ===
    col_map = {}
    for key, aliases in COLUMN_ALIASES.items():
        if key == "ho_ten":
            continue
        for i, h in enumerate(row1_cells):
            if h in aliases and key not in col_map:
                col_map[key] = i
                break

    # Neu khong tim thay ho_dem/ten rieng, tim "Ho va ten" lam 1 cot
    if "ten" not in col_map and "ho_dem" not in col_map:
        for i, h in enumerate(row1_cells):
            if _is_ho_ten_header(h):
                col_map["ho_ten_single"] = i
                return col_map, 2, "single_hoten"

    return col_map, 2, "split_cols"


def _split_ho_ten(full_name: str) -> tuple:
    """Tach 'Nguyen Van A' -> ('Nguyen Van', 'A')."""
    parts = full_name.strip().split()
    if len(parts) == 0:
        return ("", "")
    if len(parts) == 1:
        return ("", parts[0])
    return (" ".join(parts[:-1]), parts[-1])


def _safe_get(row, index):
    """Lay gia tri an toan tu row, tra ve '' neu None hoac out of range."""
    if index is None or index >= len(row):
        return ""
    val = row[index]
    return str(val).strip() if val is not None else ""


def is_attt_student(masv: str, lop: str) -> bool:
    """Kiem tra xem sinh vien co thuoc khoa ATTT khong (dua tren MASV hoac ma lop)."""
    return "AT" in masv.upper() or "AT" in lop.upper()


def import_students_from_workbook(workbook, only_attt: bool = False) -> dict:
    """
    Xu ly import tu openpyxl Workbook da mo san.
    Ho tro nhieu format Excel khac nhau.
    """
    ws = workbook.active

    result = {
        "total": 0,
        "users_created": 0,
        "users_updated": 0,
        "profiles_created": 0,
        "profiles_updated": 0,
        "skipped_not_attt": 0,
        "failed": 0,
        "errors": [],
        "log": [],
    }

    if ws.max_row is None or ws.max_row < 2:
        result["errors"].append("File Excel trong hoac khong co du lieu.")
        return result

    # === Phat hien cot thong minh ===
    col_map, data_start_row, mode = detect_columns_smart(ws)
    result["log"].append(f"[INFO] Che do nhan dien: {mode}, bat dau doc tu dong {data_start_row}")
    result["log"].append(f"[INFO] Ban do cot: {col_map}")

    # Validate cot bat buoc
    has_masv = "masv" in col_map
    has_name = ("ten" in col_map) or ("ho_ten_single" in col_map) or (mode == "merged_2col")

    if not has_masv:
        result["errors"].append(
            f"Khong tim duoc cot Ma SV. Cac cot hien co: {[ws.cell(row=1, column=c).value for c in range(1, ws.max_column+1)]}"
        )
        return result

    if not has_name:
        result["errors"].append(
            f"Khong tim duoc cot ten/ho va ten. Ban do cot: {col_map}"
        )
        return result

    # === Doc du lieu ===
    for row_idx in range(data_start_row, ws.max_row + 1):
        row = []
        for col_idx in range(1, ws.max_column + 1):
            row.append(ws.cell(row=row_idx, column=col_idx).value)

        masv = _safe_get(row, col_map.get("masv"))

        if not masv or masv in ("None", ""):
            continue

        result["total"] += 1

        # --- Xac dinh ho_dem va ten ---
        if mode == "single_hoten":
            full_name = _safe_get(row, col_map.get("ho_ten_single"))
            ho_dem, ten = _split_ho_ten(full_name)
        elif mode == "merged_2col":
            ho_dem = _safe_get(row, col_map.get("ho_dem"))
            ten = _safe_get(row, col_map.get("ten"))
        else:  # split_cols
            ho_dem = _safe_get(row, col_map.get("ho_dem"))
            ten = _safe_get(row, col_map.get("ten"))

        lop = _safe_get(row, col_map.get("lop"))

        # Loc sinh vien ATTT neu co tuy chon
        if only_attt and not is_attt_student(masv, lop):
            result["skipped_not_attt"] += 1
            continue

        try:
            user, created = User.objects.get_or_create(
                username=masv,
                defaults={
                    "role":       User.STUDENT,
                    "first_name": ten,
                    "last_name":  ho_dem,
                    "is_active":  True,
                },
            )

            if created:
                user.set_password(DEFAULT_PASSWORD)
                user.save()
                result["users_created"] += 1
                result["log"].append(f"[TAO MOI] {masv} - {ho_dem} {ten}")
            else:
                updated = False
                if user.first_name != ten:
                    user.first_name = ten
                    updated = True
                if user.last_name != ho_dem:
                    user.last_name = ho_dem
                    updated = True
                if user.role != User.STUDENT:
                    user.role = User.STUDENT
                    updated = True
                if updated:
                    user.save()
                    result["users_updated"] += 1
                    result["log"].append(f"[CAP NHAT] {masv} - {ho_dem} {ten}")

            profile, p_created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    "student_id": masv,
                    "class_name": lop,
                    "major":      "",
                    "phone":      "",
                },
            )

            if p_created:
                result["profiles_created"] += 1
            else:
                p_updated = False
                if profile.student_id != masv:
                    profile.student_id = masv
                    p_updated = True
                if profile.class_name != lop:
                    profile.class_name = lop
                    p_updated = True
                if p_updated:
                    profile.save()
                    result["profiles_updated"] += 1

        except Exception as e:
            result["failed"] += 1
            result["errors"].append(f"Loi dong {masv}: {e}")

    return result
