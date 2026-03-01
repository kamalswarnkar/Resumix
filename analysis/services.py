import logging
import os
import threading

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

try:
    from openai import OpenAI
    from openai import APITimeoutError, APIConnectionError, RateLimitError
except Exception:  # pragma: no cover
    OpenAI = None
    APITimeoutError = None
    APIConnectionError = None
    RateLimitError = None

logger = logging.getLogger(__name__)


def _should_use_ai() -> bool:
    return bool(os.getenv("OPENAI_API_KEY")) and bool(OpenAI)


def _build_ai_prompt(payload: dict) -> str:
    return (
        "You are a resume coach. Provide 4 to 6 concise, actionable improvement tips. "
        "Keep each tip to one sentence. Focus on gaps between resume and job description.\n\n"
        f"Job description:\n{payload['job_description']}\n\n"
        f"Resume summary:\n{payload['resume_excerpt']}\n\n"
        f"Scores:\n"
        f"- Match score: {payload['match_score']}%\n"
        f"- Keyword similarity: {payload['keyword_similarity']}%\n"
        f"- Skill match: {payload['skill_match_score']}%\n"
        f"- Experience relevance: {payload['experience_relevance']}%\n"
        f"- ATS compliance: {payload['ats_compliance']}%\n\n"
        f"Missing skills: {', '.join(payload['skills_missing']) or 'None'}\n"
        f"Predicted role: {payload['predicted_role'] or 'N/A'}\n\n"
        "Return only the tips as plain text lines (no numbering, no bullet symbols)."
    )


def _generate_ai_suggestions(payload: dict) -> list[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not OpenAI:
        return []

    try:
        timeout_seconds = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "4"))
        base_url = os.getenv("OPENAI_API_BASE") or None
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            max_retries=0,
            timeout=timeout_seconds,
        )
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=_build_ai_prompt(payload),
            max_output_tokens=220,
        )
        text = ""
        if response.output and response.output[0].content:
            text = response.output[0].content[0].text or ""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return lines[:6]
    except (APITimeoutError, APIConnectionError):
        logger.warning("AI suggestions timed out or connection failed.")
        return []
    except RateLimitError:
        logger.warning("AI suggestions rate-limited or out of quota.")
        return []
    except Exception:
        logger.exception("AI suggestions generation failed.")
        return []


def _append_ai_suggestions_async(analysis_id: int, payload: dict) -> None:
    try:
        from django.db import close_old_connections
        close_old_connections()
        ai_suggestions = _generate_ai_suggestions(payload)
        if not ai_suggestions:
            return
        analysis = Analysis.objects.get(id=analysis_id)
        existing = [line for line in analysis.suggestions.splitlines() if line.strip()]
        existing_set = set(existing)
        for line in ai_suggestions:
            tagged = f"AI: {line}"
            if tagged not in existing_set:
                existing.append(tagged)
        analysis.suggestions = "\n".join(existing)
        analysis.save(update_fields=["suggestions"])
    except Exception:
        logger.exception("AI async update failed.")


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

    ai_payload = {
        "job_description": job_description or "",
        "resume_excerpt": resume_text[:2000],
        "match_score": round(final_score, 2),
        "keyword_similarity": round(keyword_similarity, 2),
        "skill_match_score": round(skill_match, 2),
        "experience_relevance": round(experience_relevance, 2),
        "ats_compliance": round(ats_compliance, 2),
        "skills_missing": missing,
        "predicted_role": predicted_role,
    }
    analysis = Analysis.objects.create(
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

    use_async = os.getenv("OPENAI_ASYNC", "true").lower() in {"1", "true", "yes"}
    if _should_use_ai():
        if use_async:
            thread = threading.Thread(
                target=_append_ai_suggestions_async,
                args=(analysis.id, ai_payload),
                daemon=True,
            )
            thread.start()
        else:
            ai_suggestions = _generate_ai_suggestions(ai_payload)
            if ai_suggestions:
                analysis.suggestions = "\n".join(
                    suggestions + [f"AI: {line}" for line in ai_suggestions]
                )
                analysis.save(update_fields=["suggestions"])

    return analysis
