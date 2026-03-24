---
name: build-django-module
description: Build a Django module end-to-end
agent: agent
tools: ['search/codebase', 'editFiles', 'runCommands', 'read/problems']
---

Build a Django module in this repository.

Requirements:
- follow .github/copilot-instructions.md
- create/update models, forms, views, urls, admin, templates
- keep changes minimal and consistent with current codebase
- run migrations/checks if models change
- summarize what changed and any remaining issues