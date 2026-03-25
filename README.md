# Internship Management ATTT

Hệ thống hỗ trợ quản lý thực tập cuối khoá tại doanh nghiệp cho Khoa An toàn thông tin.

## Repository
- GitHub: [internship-management-attt](https://github.com/duycao2311/internship-management-attt)

## Mô tả đề tài
Dự án xây dựng ứng dụng hỗ trợ quản lý quy trình thực tập cuối khoá, bao gồm:
- Quản lý sinh viên đủ điều kiện thực tập
- Quản lý doanh nghiệp tiếp nhận thực tập
- Quản lý giảng viên hướng dẫn
- Theo dõi đăng ký thực tập
- Theo dõi tiến độ, báo cáo thực tập
- Đánh giá kết quả cuối kỳ

## Mục tiêu
- Số hoá quy trình thực tập cuối khoá
- Giảm thao tác quản lý thủ công
- Hỗ trợ sinh viên, giảng viên và doanh nghiệp theo dõi tiến độ dễ hơn
- Tạo nền tảng để mở rộng thêm dashboard, thống kê và báo cáo sau này

## Công nghệ sử dụng
- Python
- Django
- SQLite
- PostgreSQL
- HTML / CSS / Bootstrap

## Installation
### 1. Clone repository
```sh
git clone https://github.com/duycao2311/internship-management-attt
cd internship-management-attt
```

### 2. Set up Python environment

```sh
python -m venv .venv
source .venv\Scripts\activate      # Windows
# or
source .venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```sh
pip install -r requirements.txt
```

### 4. Khởi tạo Database và Tài khoản Admin

Vì thư mục code không đi kèm database, bạn cần chạy lệnh sau để tạo các bảng trong cơ sở dữ liệu:

```sh
python manage.py migrate
```

Sau đó, tạo tài khoản quản trị (Superuser) để đăng nhập vào hệ thống:

```sh
python manage.py createsuperuser
```

### 5. Chạy Server

```sh
python manage.py runserver
```

Truy cập vào [http://localhost:8000](http://localhost:8000) để sử dụng hệ thống.

## Chức năng dự kiến
- Đăng nhập và phân quyền
- Quản lý sinh viên
- Quản lý doanh nghiệp
- Quản lý giảng viên
- Tạo đợt thực tập
- Đăng ký / xét duyệt thực tập
- Nộp báo cáo tiến độ
- Đánh giá cuối kỳ
- Thống kê cơ bản

## Cấu trúc project
```text
internship-management-attt/
├── .venv/
├── docs/
├── screenshots/
├── src/
├── .gitignore
├── README.md
└── requirements.txt