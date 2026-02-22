import json
import os
from urllib import error, request

class AISuggestionsError(RuntimeError):
    pass


def _normalize_suggestions(raw_text: str) -> list[str]:
    if not raw_text:
        return []

    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict):
            candidates = parsed.get("suggestions", [])
        elif isinstance(parsed, list):
            candidates = parsed
        else:
            candidates = []
        if isinstance(candidates, list):
            return [str(item).strip() for item in candidates if str(item).strip()][:6]
    except json.JSONDecodeError:
        pass

    lines = [line.strip("- ").strip() for line in raw_text.splitlines() if line.strip()]
    return lines[:6]


def generate_suggestions_with_ai(
    resume_text: str,
    job_description: str,
    missing_skills: list[str],
    ats_score: float,
    exp_score: float,
    match_score: float,
) -> list[str]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise AISuggestionsError("OPENAI_API_KEY is missing. AI suggestions are required.")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    api_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")

    payload = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert resume coach. Return only JSON with key "
                    "\"suggestions\" as an array of 3-6 concise actionable bullets."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Resume excerpt: {resume_text[:1500]}\n\n"
                    f"Job description: {job_description[:1500]}\n\n"
                    f"Missing skills: {', '.join(missing_skills) if missing_skills else 'none'}\n"
                    f"ATS score: {ats_score}\n"
                    f"Experience relevance: {exp_score}\n"
                    f"Overall match score: {match_score}\n\n"
                    "Respond with strict JSON format: "
                    "{\"suggestions\": [\"...\", \"...\", \"...\"]}"
                ),
            },
        ],
    }

    req = request.Request(
        url=f"{api_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    last_error = None
    for _ in range(2):
        try:
            with request.urlopen(req, timeout=25) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            suggestions = _normalize_suggestions(content)
            if suggestions:
                return suggestions
            last_error = "AI returned empty suggestions."
        except (
            error.URLError,
            error.HTTPError,
            KeyError,
            IndexError,
            json.JSONDecodeError,
            TimeoutError,
        ) as exc:
            last_error = str(exc)

    raise AISuggestionsError(
        "AI suggestions request failed. Verify OPENAI_API_KEY, OPENAI_MODEL, "
        "OPENAI_API_BASE, network access, and model permissions."
        + (f" Last error: {last_error}" if last_error else "")
    )
