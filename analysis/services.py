from resumes.models import Resume
from .models import Analysis
from ml.services import predict_role
from utils.nlp import (
    extract_skills,
    keyword_similarity_score,
    experience_relevance_score,
    ats_compliance_score,
    generate_suggestions,
)


def run_analysis(resume: Resume, job_description: str) -> Analysis:
    resume_text = resume.extracted_text or ""

    keyword_similarity = keyword_similarity_score(resume_text, job_description)

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    if jd_skills:
        overlap = set(resume_skills).intersection(set(jd_skills))
        skill_match = (len(overlap) / len(set(jd_skills))) * 100
        missing = sorted(list(set(jd_skills) - set(resume_skills)))
    else:
        skill_match = 0.0
        missing = []

    experience_relevance = experience_relevance_score(resume_text, job_description)
    ats_compliance = ats_compliance_score(resume_text)

    final_score = (
        keyword_similarity * 0.40
        + skill_match * 0.30
        + experience_relevance * 0.20
        + ats_compliance * 0.10
    )

    predicted_role = predict_role(resume_text)
    suggestions = generate_suggestions(missing, ats_compliance, experience_relevance)

    return Analysis.objects.create(
        resume=resume,
        job_description=job_description,
        match_score=round(final_score, 2),
        keyword_similarity=round(keyword_similarity, 2),
        skill_match_score=round(skill_match, 2),
        experience_relevance=round(experience_relevance, 2),
        ats_compliance=round(ats_compliance, 2),
        skills_found=sorted(list(set(resume_skills))),
        skills_missing=missing,
        suggestions="\n".join(suggestions),
        predicted_role=predicted_role,
    )
