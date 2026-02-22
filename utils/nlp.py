import json
import re
from pathlib import Path

import nltk
import spacy
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


for resource in ("stopwords", "punkt"):
    try:
        nltk.data.find(f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

STOPWORDS = set(stopwords.words("english"))

try:
    NLP = spacy.load("en_core_web_sm")
except OSError:
    NLP = spacy.blank("en")

SKILLS_FILE = Path(__file__).resolve().parent / "skills.json"


def _load_skills():
    with open(SKILLS_FILE, "r", encoding="utf-8") as file:
        return set(json.load(file)["skills"])


KNOWN_SKILLS = _load_skills()


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_text(text: str) -> str:
    cleaned = clean_text(text)
    doc = NLP(cleaned)
    tokens = []
    for token in doc:
        lemma = token.lemma_.strip() if token.lemma_ else token.text.strip()
        if lemma and lemma not in STOPWORDS and not token.is_space:
            tokens.append(lemma)
    return " ".join(tokens)


def keyword_similarity_score(resume_text: str, job_description: str) -> float:
    p_resume = preprocess_text(resume_text)
    p_jd = preprocess_text(job_description)

    if not p_resume or not p_jd:
        return 0.0

    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform([p_resume, p_jd])
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return max(0.0, min(score * 100, 100.0))


def extract_skills(text: str):
    cleaned = clean_text(text)
    found = {skill for skill in KNOWN_SKILLS if skill in cleaned}

    doc = NLP(cleaned)
    for ent in doc.ents:
        candidate = ent.text.strip().lower()
        if candidate in KNOWN_SKILLS:
            found.add(candidate)

    return sorted(found)


def experience_relevance_score(resume_text: str, job_description: str) -> float:
    resume_years = _extract_years(resume_text)
    jd_years = _extract_years(job_description)

    if jd_years == 0:
        return 70.0
    if resume_years == 0:
        return 20.0

    ratio = min(resume_years / jd_years, 1.25)
    return max(0.0, min(ratio * 80, 100.0))


def ats_compliance_score(resume_text: str) -> float:
    text = clean_text(resume_text)
    sections = ["experience", "education", "skills", "projects", "summary"]
    section_points = sum(1 for section in sections if section in text) / len(sections) * 70

    has_email = 1 if re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", resume_text) else 0
    has_phone = 1 if re.search(r"\+?\d[\d\s\-]{8,}\d", resume_text) else 0
    contact_points = (has_email + has_phone) / 2 * 20

    length_points = 10 if 300 <= len(text.split()) <= 1200 else 5
    return round(section_points + contact_points + length_points, 2)


def _extract_years(text: str) -> int:
    matches = re.findall(r"(\d+)\+?\s+years?", text.lower())
    if not matches:
        return 0
    return max(int(v) for v in matches)


def generate_suggestions(missing_skills, ats_score: float, exp_score: float) -> list[str]:
    tips = []
    if missing_skills:
        tips.append("Add or strengthen these skills: " + ", ".join(missing_skills[:10]))
    if ats_score < 70:
        tips.append("Improve ATS structure with clear sections and contact details.")
    if exp_score < 60:
        tips.append("Highlight impact, tenure, and domain-relevant accomplishments.")
    if not tips:
        tips.append("Strong profile overall. Tailor keywords to each job posting.")
    return tips
