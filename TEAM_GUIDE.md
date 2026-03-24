# Hướng dẫn dự án cho thành viên team

## 1. Cấu trúc dự án hiện tại
- **accounts/**: Xử lý xác thực, phân quyền, profile, dashboard cho từng vai trò.
- **templates/**: Giao diện dùng chung (base.html, includes/)
- **static/**: File CSS, JS, hình ảnh dùng chung
- **apps/accounts/templates/accounts/**: Template riêng cho từng vai trò/profile

## 2. Những gì person 1 đã hoàn thành
- Xây dựng custom user model và các profile riêng cho từng vai trò (Student, Department, Lecturer)
- Đã có login/logout, dashboard phân vai trò, profile cho từng loại user
- Đã chuẩn hóa layout base.html, navbar, sidebar, messages
- Đã tạo sẵn các file static (css/js) và hướng dẫn đặt tên
- Đã bảo vệ route theo vai trò, redirect hợp lý

## 3. File dùng chung (KHÔNG tự ý sửa nếu không chắc):
- `templates/base.html`, `templates/includes/*`
- `static/css/base.css`, `static/js/base.js`, `static/images/logo-ptit.jpg`, `logo-attt.jpg`
- `accounts/models.py`, `accounts/views.py`, `accounts/urls.py`

## 4. Cách mở rộng giao diện
- Luôn kế thừa `base.html`:
  ```django
  {% extends 'base.html' %}
  {% block title %}Tên trang{% endblock %}
  {% block content %}
    <!-- Nội dung -->
  {% endblock %}
  ```
- Đặt template module vào `apps/<module>/templates/<module>/`
- Đặt css/js module vào `static/css/<ten_module>.css`, `static/js/<ten_module>.js`
- Thêm vào template qua block `extra_css` hoặc `extra_js`

## 5. Quy tắc đặt tên url & role
- Tên url: `<module>_<tính_năng>` (vd: `accounts_login`, `recruitment_post_list`)
- Tên role: `student`, `department`, `lecturer`, `admin` (dùng đúng như trong models.User)

## 6. Bảo vệ quyền truy cập
- Dùng decorator `@role_required` (đã có sẵn trong accounts/views.py)
- Nếu không đúng vai trò, sẽ redirect về forbidden hoặc dashboard phù hợp

## 7. Lưu ý
- Không xóa/sửa file dùng chung nếu không chắc chắn
- Luôn kiểm tra lại giao diện trên nhiều vai trò
- Đọc kỹ README.md và DEV_GUIDE.md trước khi phát triển module mới
