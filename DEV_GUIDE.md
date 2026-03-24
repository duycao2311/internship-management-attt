# Hướng dẫn phát triển giao diện (Frontend)

## 1. Kế thừa base.html
- Mọi template đều nên kế thừa từ `base.html` để đảm bảo giao diện đồng nhất.
- Ví dụ:
  ```django
  {% extends 'base.html' %}
  {% block title %}Tên trang{% endblock %}
  {% block content %}
    <!-- Nội dung trang -->
  {% endblock %}
  ```
- Có thể sử dụng các block: `title`, `content`, `extra_css`, `extra_js`.

## 2. Đặt template ở đâu?
- Template của từng module đặt trong `apps/<module>/templates/<module>/`.
- Template dùng chung đặt ở `templates/` hoặc `templates/includes/`.

## 3. Đặt file CSS/JS ở đâu?
- File CSS/JS dùng chung: `static/css/base.css`, `static/js/base.js`.
- File CSS/JS riêng cho từng module: `static/css/<ten_module>.css`, `static/js/<ten_module>.js`.
- Khi cần, thêm vào template qua block `extra_css` hoặc `extra_js`.

## 4. Đặt tên url như thế nào?
- Đặt tên url theo dạng: `<module>_<tính_năng>` (ví dụ: `accounts_login`, `recruitment_post_list`).
- Đăng ký url trong file `urls.py` của từng app, sau đó include vào `urls.py` chính.

## 5. Bảo vệ quyền truy cập (role protection)
- Sử dụng decorator `@role_required` hoặc các helper đã có trong `accounts/decorators.py`.
- Nếu không đúng vai trò, redirect về trang forbidden hoặc dashboard phù hợp.

## 6. Ghi chú mở rộng
- Đặt comment rõ ràng trong template để các thành viên biết chỗ mở rộng nội dung.
- Luôn kiểm tra lại giao diện trên nhiều vai trò khác nhau.
