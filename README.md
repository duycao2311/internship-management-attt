# Internship Management System

> A role-based web platform for managing the complete internship lifecycle of
> PTIT Information Security students.

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Database](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

## Overview

The Internship Management System centralizes internship recruitment,
placement, supervision, reporting, grading, and progress tracking in one
application. It provides dedicated workflows for students, partner companies,
company mentors, lecturers, and system administrators.

The project was developed for the Information Security program at the Posts
and Telecommunications Institute of Technology (PTIT).

## Key Features

### Recruitment and placement

- Companies can create, update, close, and manage internship postings.
- Students can maintain multiple CVs and apply to available positions.
- Companies can review applications and accept or reject candidates.
- Students can confirm an accepted placement.
- Students who find an internship independently can submit an external
  placement request for administrator approval.

### Internship administration

- Role-based authentication and dashboards for five user types.
- Internship term configuration with start and end dates.
- Student import from `.xlsx` files with support for several common column
  layouts.
- Company-to-lecturer mappings and individual internship assignments.
- Automatic mentor-group allocation with configurable capacity.
- Separate handling of partner-company and external internships.

### Reporting and assessment

- Ten weekly reports and one final report per internship assignment.
- Configurable weekly and final-report deadlines.
- Late-submission tracking and report locking.
- Independent grading by company mentors and lecturers.
- Threaded comments and replies on submitted reports.
- Moodle-style views for reviewing and grading submissions efficiently.
- Statistics dashboard with filters, progress indicators, risk flags, and
  Excel export.

## User Roles

| Role | Main responsibilities |
| --- | --- |
| Student | Browse positions, manage CVs, apply, confirm a placement, and submit reports |
| Company | Publish internship positions and review student applications |
| Mentor | Supervise assigned groups, comment on reports, and provide company-side grades |
| Lecturer | Monitor assigned students, manage deadlines, provide feedback, and grade reports |
| Administrator | Configure terms, import students, approve external placements, and manage assignments |

## Technology Stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3.11+, Django 5.2 |
| Frontend | Django Templates, HTML5, CSS3, JavaScript, Bootstrap Icons |
| Database | SQLite |
| Spreadsheet processing | openpyxl |
| Configuration | python-decouple |

## Project Structure

```text
internship-management-attt/
├── apps/
│   ├── accounts/       # Authentication, profiles, roles, imports, and admin workflows
│   ├── recruitment/    # Posts, CVs, applications, and external placements
│   └── reports/        # Terms, assignments, deadlines, reports, grading, and statistics
├── static/             # Stylesheets, JavaScript, images, and the import template
├── templates/          # Shared layouts and UI components
├── stellar_core/       # Django project configuration
├── manage.py
├── requirements.txt
└── seed_data.py        # Optional development data
```

## Getting Started

### Prerequisites

- Python 3.11 or newer
- `pip`
- Git

SQLite is included with Python, so no separate database server is required.

### Installation

1. Clone the repository and enter the project directory.

   ```bash
   git clone https://github.com/duycao2311/internship-management-attt.git
   cd internship-management-attt
   ```

2. Create a virtual environment.

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment.

   Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   Windows Command Prompt:

   ```cmd
   .venv\Scripts\activate.bat
   ```

   macOS or Linux:

   ```bash
   source .venv/bin/activate
   ```

4. Install the dependencies.

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Apply the database migrations.

   ```bash
   python manage.py migrate
   ```

6. Create an administrator account.

   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server.

   ```bash
   python manage.py runserver
   ```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a browser. The
Django administration site is available at
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

## Optional Demo Data

To populate a local database with sample users, internship posts, assignments,
deadlines, and reports, run:

```bash
python manage.py shell -c "exec(open('seed_data.py', encoding='utf-8').read())"
```

The script prints the generated development accounts when it finishes.
These accounts use a shared demo password and must never be used in a
production environment.

## Importing Students

Administrators can import students through the web dashboard or with the
management command:

```bash
python manage.py import_students_from_excel path/to/students.xlsx
```

Supported workbooks may contain separate student ID, surname, given-name, and
class columns, or a combined full-name column. A sample workbook is available
at `static/xlss/D23-EXPORT.xlsx`.

## Development Checks

Run Django's built-in validation before submitting changes:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
```

## Data and Security Notes

- The application is configured for local development by default.
- Local SQLite databases, environment files, virtual environments, caches, and
  user-uploaded media are excluded from version control.
- Uploaded CVs and report attachments are stored under `media/`; only their
  paths are stored in the database.
- Use environment-specific secrets, disable debug mode, configure allowed
  hosts, and use production-grade static/media storage before deployment.
- Change all seeded passwords immediately if sample data is used outside an
  isolated development environment.

## Maintainer

[duycao2311](https://github.com/duycao2311)
