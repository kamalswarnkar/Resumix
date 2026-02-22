# Resumix - AI Resume Analyzer

Production-oriented Django + DRF application for resume-to-job matching and role prediction, now delivered through a Django template UI (no separate React frontend required).

## Stack
- Python 3.11+
- Django 5 + DRF
- PostgreSQL
- JWT auth (`simplejwt`)
- spaCy + NLTK + scikit-learn
- pdfplumber + python-docx
- Celery + Redis ready

## 1. Setup Backend
1. Open terminal at `C:\Users\swarn\OneDrive\Desktop\Resumix`.
2. Activate env:
   - PowerShell: `newenv311\Scripts\Activate.ps1`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Create env file:
   - copy `.env.example` to `.env`
5. Download NLP resources:
   - `python -m nltk.downloader stopwords punkt`
   - `python -m spacy download en_core_web_sm`
6. Create PostgreSQL database (`resume_db`) and update `.env` credentials.
7. Run migrations:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
8. Create admin user:
   - `python manage.py createsuperuser`
9. Start backend:
   - `python manage.py runserver`
10. Open app UI:
   - `http://127.0.0.1:8000/`

## AI Suggestions Setup (Required)
AI suggestions are now strict AI-only (no rule-based fallback). Configure these keys in `.env`:
- `OPENAI_API_KEY=your_api_key`
- `OPENAI_MODEL=gpt-4o-mini`
- `OPENAI_API_BASE=https://api.openai.com/v1`

If AI configuration or API access fails, `/api/resume/analyze/` returns `503` with an error message.

## 2. Train ML Model
1. Ensure backend dependencies are installed.
2. Run:
   - `python ml\training\train_model.py`
3. Generated artifacts:
   - `ml\artifacts\tfidf_vectorizer.pkl`
   - `ml\artifacts\role_classifier.pkl`
   - `ml\artifacts\label_encoder.pkl`

## 3. Main API Endpoints
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/resume/upload/`
- `POST /api/resume/analyze/`
- `GET /api/resume/history/`
- `GET /api/admin/users/`
- `GET /api/admin/stats/`

## 4. Scoring Formula
`Final Score = (Keyword Similarity * 0.4) + (Skill Match * 0.3) + (Experience Relevance * 0.2) + (ATS Compliance * 0.1)`

## 5. Swagger Docs
- `GET /api/docs/`
