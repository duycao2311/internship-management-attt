---
name: instruction
description: Read this first before start the project
---
# Project rules

- This is a Django internship management system.
- Use server-rendered Django templates first, not React.
- Keep code beginner-friendly and maintainable.
- Use app separation:
  - accounts: auth, roles, profiles
  - recruitment: internship posts, applications, CVs
  - reports: weekly/midterm/final reports
  - evaluations: lecturer and department evaluations
- Prefer class-based views only when it clearly improves readability; otherwise use simple function-based views.
- Always update urls.py, admin.py, forms.py, and templates when creating a new feature.
- Use Bootstrap or simple CSS first; avoid overengineering frontend.
- Before changing models, explain migration impact.
- After edits, run:
  - python manage.py makemigrations
  - python manage.py migrate
  - python manage.py check
- Never delete existing files unless asked.
- If unsure, ask before making architecture-breaking changes.