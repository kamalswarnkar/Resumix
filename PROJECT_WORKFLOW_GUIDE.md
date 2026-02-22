# Resumix Project Workflow (Complete Build + File Map)

## 1. What This Project Does
Resumix is a Django + DRF application for resume analysis.
It supports user registration/login, resume upload/parsing, scoring against a job description, predicted role classification, history tracking, and admin stats APIs.
The current UI is template-based (no separate React frontend runtime).

## 2. End-to-End Runtime Workflow
1. User lands on `/` (`frontend_template.html`).
2. User registers (`/register/`) and logs in (`/login/`) using JWT auth endpoints.
3. After login, user reaches `/dashboard/`.
4. User uploads resume on `/upload/` (`/api/resume/upload/`).
5. User runs analysis on `/analysis/` (`/api/resume/analyze/`).
6. Backend parses resume text, computes scores, predicts role, stores analysis record.
7. Dashboard fetches `/api/resume/history/` and renders recent analysis records.
8. Admin endpoints are available at `/api/admin/users/` and `/api/admin/stats/` for admin-role users.

## 3. Windows Terminal Commands Used in This Project

### 3.1 Initial setup
```powershell
cd C:\Users\swarn\OneDrive\Desktop\Resumix
newenv311\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3.2 NLP resource setup
```powershell
python -m nltk.downloader stopwords punkt
python -m spacy download en_core_web_sm
```

### 3.3 Database + migrations
```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py showmigrations analysis
python manage.py migrate analysis
```

### 3.4 Run + checks
```powershell
python manage.py runserver
python manage.py check
python manage.py makemigrations --check
```

### 3.5 ML training
```powershell
python ml\training\train_model.py
```

### 3.6 Common debugging commands used during development
```powershell
rg --files -g "*.py"
rg --files templates
rg -n "pattern" -S
Get-Content <file_path>
git status --short
python manage.py shell -c "from analysis.models import Analysis; print('analyses:', Analysis.objects.count())"
```

## 4. Environment Variables (`.env`)
```env
DJANGO_SECRET_KEY=replace-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

POSTGRES_DB=resume_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=7

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

## 5. Python/Django File-by-File Role Map

### 5.1 Root and project package
| File | Role |
|---|---|
| `manage.py` | Django command entry point (`runserver`, `migrate`, etc.). |
| `resume_analyzer/__init__.py` | Package marker. |
| `resume_analyzer/asgi.py` | ASGI app entry for async deployments. |
| `resume_analyzer/wsgi.py` | WSGI app entry for sync deployments. |
| `resume_analyzer/settings.py` | Core configuration: apps, DB, JWT, templates, static/media, logging. |
| `resume_analyzer/urls.py` | Global URL routing for pages, APIs, docs, admin. |
| `resume_analyzer/views.py` | Template `TemplateView` classes for landing/register/login/dashboard/upload/analysis pages. |
| `resume_analyzer/celery.py` | Celery app bootstrap (broker/result backend integration point). |

### 5.2 Users app
| File | Role |
|---|---|
| `users/__init__.py` | Package marker. |
| `users/apps.py` | Django app config for users app. |
| `users/admin.py` | Admin registration hooks (if defined). |
| `users/models.py` | Custom `User` model (email login + role field). |
| `users/managers.py` | `create_user` / `create_superuser` manager logic. |
| `users/serializers.py` | Register/login validation + user serialization. |
| `users/views.py` | Auth endpoints (`register`, `login`) returning JWT tokens. |
| `users/urls.py` | Auth routes including token refresh. |
| `users/permissions.py` | Custom role-based permission (`IsAdminRole`). |
| `users/migrations/0001_initial.py` | Initial users schema migration. |
| `users/migrations/0002_user_is_superuser_alter_user_date_joined_and_more.py` | Users schema alterations. |
| `users/migrations/__init__.py` | Migration package marker. |

### 5.3 Resumes app
| File | Role |
|---|---|
| `resumes/__init__.py` | Package marker. |
| `resumes/apps.py` | Django app config for resumes app. |
| `resumes/admin.py` | Admin registration hooks (if defined). |
| `resumes/models.py` | `Resume` model (file, extracted text, timestamps, user FK). |
| `resumes/serializers.py` | Upload and analyze request serializers. |
| `resumes/validators.py` | File type and file size validation. |
| `resumes/parsers.py` | PDF/DOCX text extraction. |
| `resumes/views.py` | Upload/analyze/history DRF endpoints. |
| `resumes/urls.py` | Resume API routing. |
| `resumes/migrations/0001_initial.py` | Initial resumes schema migration. |
| `resumes/migrations/__init__.py` | Migration package marker. |

### 5.4 Analysis app
| File | Role |
|---|---|
| `analysis/__init__.py` | Package marker. |
| `analysis/apps.py` | Django app config for analysis app. |
| `analysis/admin.py` | Admin registration hooks (if defined). |
| `analysis/models.py` | `Analysis` model storing scores, skills, suggestions, predicted role, job description. |
| `analysis/services.py` | Main scoring pipeline and persistence (`run_analysis`). |
| `analysis/serializers.py` | Analysis response format (includes `suggestions_list`). |
| `analysis/admin_urls.py` | Admin-only APIs (`users`, `stats`). |
| `analysis/ai_suggestions.py` | Deprecated/unused module retained on disk; AI path removed from active code. |
| `analysis/migrations/0001_initial.py` | Initial analysis schema migration. |
| `analysis/migrations/0002_analysis_job_description.py` | Added `job_description` field. |
| `analysis/migrations/__init__.py` | Migration package marker. |

### 5.5 ML app
| File | Role |
|---|---|
| `ml/__init__.py` | Package marker. |
| `ml/apps.py` | Django app config for ML app. |
| `ml/services.py` | Loads artifacts and predicts role for resume text. |
| `ml/training/__init__.py` | Training package marker. |
| `ml/training/train_model.py` | Model training script (vectorization, candidate models, model selection, artifact save). |
| `ml/training/sample_dataset.csv` | Training data used by `train_model.py`. |

### 5.6 Utils
| File | Role |
|---|---|
| `utils/__init__.py` | Package marker. |
| `utils/nlp.py` | Text preprocessing, similarity, skill extraction, ATS score, experience score, fallback suggestions logic. |

## 6. Django Template File Roles
| File | Role |
|---|---|
| `templates/base_public.html` | Shared layout/styles for landing/register/login pages. |
| `templates/base_app.html` | Shared layout/styles + authenticated navbar + session JS helpers. |
| `templates/frontend_template.html` | Landing page. |
| `templates/register.html` | Registration UI + register API call logic. |
| `templates/login.html` | Login UI + JWT storage + fresh-login handling. |
| `templates/dashboard.html` | Dashboard metrics + history listing + per-result analysis link. |
| `templates/upload.html` | Resume upload UI + upload-state handling (`resumix_uploaded_ready`). |
| `templates/analysis.html` | Analysis form + results rendering + previous analysis loading. |

## 7. API Endpoint Summary
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/resume/upload/`
- `POST /api/resume/analyze/`
- `GET /api/resume/history/`
- `GET /api/admin/users/`
- `GET /api/admin/stats/`
- `GET /api/schema/`
- `GET /api/docs/`

## 8. Notes
- Current suggestions are fallback rule-based (not active external AI integration).
- `analysis/ai_suggestions.py` can be deleted safely when file lock/permission issue is resolved.
- After schema changes, always run `python manage.py migrate` before testing API flows.
