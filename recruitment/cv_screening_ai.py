"""
recruitment/cv_screening_ai.py

AI-powered CV screening with a three-tier fallback chain:
  1. Groq  — llama-3.1-8b-instant  (primary, GROQ_API_KEY)
  2. OpenRouter — deepseek/deepseek-chat  (secondary, OPENROUTER_API_KEY)
  3. Regex — rule-based extraction  (last resort, no key needed)
"""

import json
import os
import re

from django.conf import settings

from recruitment.models import Candidate, CandidateScreeningProfile


# ── Shared extraction prompt ──────────────────────────────────────────────────

def _build_prompt(cv_content, job_requirements):
    return f"""You are a senior HR evaluator scoring a candidate's submitted documents (CV, resume, cover letter) against a job requirement using the ONEIC Document Evaluation Form (HR&A/IAF/3.0/17).

Submitted Documents:
{cv_content}

Job Requirements:
{job_requirements}

STEP 1 — Extract all facts from the submitted documents (CV, resume, cover letter, portfolio, or any other uploaded materials).
STEP 2 — Score the candidate on each of the 8 ONEIC criteria based ONLY on what is observable in the documents (1–10 each, max total = 80):
  1. work_experience: Relevance and depth of work history, years of experience, industry alignment, job stability
  2. qualifications: Academic degrees, professional certifications, training courses relevant to the role
  3. technical_skills: Hard skills match with job requirements — tools, technologies, domain-specific competencies
  4. career_progression: Growth trajectory visible in the CV — promotions, expanding scope/seniority, increasing responsibility over time
  5. achievements_impact: Quantified accomplishments, measurable results, notable projects, awards, or recognitions listed in the documents
  6. role_relevance: Overall alignment of the candidate's background with the specific job description and requirements
  7. document_quality: Clarity, structure, and professionalism of the CV and cover letter — how well the candidate presents themselves on paper
  8. industry_knowledge: Evidence of domain expertise, sector-specific knowledge, or industry experience relevant to the role

STEP 3 — Compute grand_total (sum of all 8) and percentage (grand_total/80*100).
STEP 4 — Apply ONEIC thresholds:
  - percentage >= 70  → recommendation = "auto-shortlist"  (Suitable)
  - percentage >= 60  → recommendation = "interview"       (Standby)
  - percentage < 60   → recommendation = "reject"          (Rejected)

For years_experience: carefully count total years across ALL previous_positions. Sum durations. Do NOT return 0 unless the candidate has no work history at all.

Return ONLY valid JSON:
{{
    "candidate_name": "full name or empty string",
    "nationality": "nationality or empty string",
    "present_employer": "current/most recent employer or empty string",
    "marital_status": "single/married/divorced/widowed or empty string",
    "date_of_birth": "YYYY-MM-DD or null",
    "place_of_birth": "city or country or empty string",
    "qualification_academic": "highest academic degree e.g. Bachelor of Engineering",
    "qualification_professional": "professional certifications or empty string",
    "experience_local_years": null,
    "experience_overseas_years": null,
    "lang_arabic": false,
    "lang_english": false,
    "lang_others": "comma-separated other languages or empty string",
    "driving_license": "light/heavy/both/none",
    "skills": ["skill1", "skill2"],
    "years_experience": 0,
    "education": [{{"degree": "Bachelor", "field": "Computer Science", "institution": "University"}}],
    "previous_positions": [{{"title": "Engineer", "company": "Acme", "duration": "2 years"}}],
    "matching_score": 0,
    "matching_skills": [],
    "missing_skills": [],
    "summary": "2-3 sentence overall assessment based on the submitted documents",
    "recommendation": "auto-shortlist/interview/reject",
    "scoring_breakdown": {{
        "work_experience":    {{"score": 0, "comment": "one sentence based on CV/resume"}},
        "qualifications":     {{"score": 0, "comment": "one sentence based on CV/resume"}},
        "technical_skills":   {{"score": 0, "comment": "one sentence based on CV/resume"}},
        "career_progression": {{"score": 0, "comment": "one sentence based on CV/resume"}},
        "achievements_impact":{{"score": 0, "comment": "one sentence based on CV/resume"}},
        "role_relevance":     {{"score": 0, "comment": "one sentence based on CV/resume"}},
        "document_quality":   {{"score": 0, "comment": "one sentence based on CV/cover letter"}},
        "industry_knowledge": {{"score": 0, "comment": "one sentence based on CV/resume"}}
    }},
    "grand_total": 0,
    "percentage": 0.0,
    "ai_reasoning": "2-3 sentences explaining the final recommendation decision based on the submitted documents"
}}

Return JSON only — no markdown, no explanation."""


# ── Tier 1: Groq ─────────────────────────────────────────────────────────────

def _analyze_with_groq(cv_content, job_requirements):
    """Primary: Groq llama-3.1-8b-instant."""
    api_key = getattr(settings, "GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": _build_prompt(cv_content, job_requirements)}],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=2000,
        )
        raw = res.choices[0].message.content
        return json.loads(raw)
    except Exception as e:
        print(f"[CV Screening] Groq failed: {e}")
        return None


# ── Tier 2: OpenRouter / DeepSeek ────────────────────────────────────────────

def _analyze_with_openrouter(cv_content, job_requirements):
    """Secondary: DeepSeek via OpenRouter."""
    import requests as _requests
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        return None
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek/deepseek-chat",
            "messages": [{"role": "user", "content": _build_prompt(cv_content, job_requirements)}],
            "temperature": 0.3,
            "max_tokens": 2000,
        }
        response = _requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except Exception as e:
        print(f"[CV Screening] OpenRouter/DeepSeek failed: {e}")
        return None


# ── Tier 3: regex fallback ────────────────────────────────────────────────────

def _analyze_with_regex(cv_content, job_requirements):
    """Last resort: rule-based extraction — no AI key required."""
    try:
        from recruitment.cv_screening_fallback import mock_analyze_cv
        return mock_analyze_cv(cv_content, job_requirements)
    except Exception as e:
        print(f"[CV Screening] Regex fallback failed: {e}")
        return None


# ── Unified analyzer ──────────────────────────────────────────────────────────

def _analyze_cv(cv_content, job_requirements):
    """Try Groq → OpenRouter → regex in order, return first successful result."""
    result = _analyze_with_groq(cv_content, job_requirements)
    if result:
        result["_ai_model"] = "groq/llama-3.1-8b-instant"
        return result

    result = _analyze_with_openrouter(cv_content, job_requirements)
    if result:
        result["_ai_model"] = "openrouter/deepseek-chat"
        return result

    result = _analyze_with_regex(cv_content, job_requirements)
    if result:
        result["_ai_model"] = "regex-fallback"
        return result

    return None


# ── File text extraction ──────────────────────────────────────────────────────

def _extract_text(file_path):
    """Extract plain text from PDF, DOCX, or plain text file."""
    try:
        if file_path.endswith(".pdf"):
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "".join(page.extract_text() or "" for page in reader.pages)
        elif file_path.endswith(".docx"):
            from docx import Document
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"[CV Screening] Text extraction failed for {file_path}: {e}")
        return ""


# ── Legacy class (kept for auto_shortlist compatibility) ──────────────────────

class CVScreeningAI:
    """Thin wrapper kept for backward compatibility with auto_shortlist callers."""

    def extract_cv_content(self, cv_file_path):
        return _extract_text(cv_file_path)

    def analyze_cv_with_deepseek(self, cv_content, job_requirements):
        return _analyze_cv(cv_content, job_requirements)

    def rank_candidates(self, candidates_analysis):
        return sorted(candidates_analysis, key=lambda x: x.get("matching_score", 0), reverse=True)

    def auto_shortlist(self, candidate_ids, job_requirements, threshold=70):
        shortlisted = []
        for candidate_id in candidate_ids:
            candidate = Candidate.objects.get(pk=candidate_id)
            if candidate.resume:
                content = _extract_text(candidate.resume.path)
                analysis = _analyze_cv(content, job_requirements)
                if analysis and analysis.get("matching_score", 0) >= threshold:
                    shortlisted.append({
                        "candidate": candidate,
                        "analysis": analysis,
                        "score": analysis.get("matching_score"),
                    })
                    candidate.is_shortlisted = True
                    candidate.screening_score = analysis.get("matching_score", 0)
                    candidate.save()
        return shortlisted


# ── Main entry point ──────────────────────────────────────────────────────────

def screen_candidate_cv(candidate_id, job_requirements):
    """
    Analyze the candidate's resume using the AI chain (Groq → OpenRouter → regex)
    and save all extracted fields to CandidateScreeningProfile.
    Only the resume is used for extraction.
    """
    candidate = Candidate.objects.get(pk=candidate_id)

    if not candidate.resume:
        return None

    resume_content = _extract_text(candidate.resume.path)
    merged = _analyze_cv(resume_content, job_requirements)

    if not merged:
        return None

    # ── Derive composite score from ONEIC grand_total if available ────────────
    # The prompt now returns grand_total (/80) and percentage (/100).
    # Fall back to matching_score if those fields are missing (older cached results).
    percentage = float(merged.get("percentage", 0))
    grand_total = float(merged.get("grand_total", 0))

    if percentage > 0:
        composite_score = round(percentage)
    elif grand_total > 0:
        composite_score = round(grand_total / 80 * 100)
    else:
        composite_score = float(merged.get("matching_score", 0))

    # Derive from signals when AI returned 0
    if composite_score == 0:
        rec = str(merged.get("recommendation", "")).lower().replace("-", "_")
        matching = merged.get("matching_skills") or []
        missing = merged.get("missing_skills") or []
        extracted = merged.get("skills") or []
        total = len(matching) + len(missing)
        if total > 0:
            composite_score = round(len(matching) / total * 100)
        elif rec in ("auto_shortlist", "auto-shortlist"):
            composite_score = 75.0
        elif rec == "interview":
            composite_score = 64.0
        elif rec == "reject":
            composite_score = 45.0
        elif extracted:
            composite_score = 55.0

    # ── Apply ONEIC thresholds to set recommendation ───────────────────────
    if composite_score >= 70:
        derived_rec = "auto_shortlist"
    elif composite_score >= 60:
        derived_rec = "interview"
    else:
        derived_rec = "reject"

    # Prefer AI recommendation if it already matches thresholds; override if not
    ai_rec = str(merged.get("recommendation", "")).lower().replace("-", "_").replace(" ", "_")
    if ai_rec in ("auto_shortlist", "interview", "reject"):
        # Use ONEIC-threshold-derived value since the prompt already applies them
        recommendation = derived_rec
    else:
        recommendation = derived_rec

    from datetime import datetime

    # ── Fix experience: sum previous_positions durations if AI returned 0 ──
    years_exp = int(merged.get("years_experience") or 0)
    if years_exp == 0:
        positions = merged.get("previous_positions") or []
        total_months = 0
        dur_re = re.compile(r'(\d+(?:\.\d+)?)\s*(year|yr|month|mo)', re.I)
        for pos in positions:
            dur = str(pos.get("duration", ""))
            for num, unit in dur_re.findall(dur):
                n = float(num)
                if "month" in unit.lower() or "mo" in unit.lower():
                    total_months += n
                else:
                    total_months += n * 12
        if total_months > 0:
            years_exp = max(1, round(total_months / 12))

    profile, _ = CandidateScreeningProfile.objects.get_or_create(candidate=candidate)
    profile.extracted_skills = merged.get("skills", [])
    profile.years_experience = years_exp
    profile.education = merged.get("education", [])
    profile.previous_positions = merged.get("previous_positions", [])
    profile.matching_score = composite_score
    profile.matching_skills = merged.get("matching_skills", [])
    profile.missing_skills = merged.get("missing_skills", [])
    profile.summary = merged.get("summary", "")
    profile.recommendation = recommendation
    profile.status = "screened"
    profile.ai_model = merged.get("_ai_model", "")

    # ONEIC scoring breakdown + reasoning
    import json as _json
    breakdown = merged.get("scoring_breakdown") or {}
    if breakdown:
        profile.scoring_breakdown = breakdown if isinstance(breakdown, dict) else {}
    profile.ai_reasoning = merged.get("ai_reasoning", "") or ""
    profile.oneic_grand_total = grand_total or 0
    profile.oneic_percentage = composite_score

    # Personal details (resume-priority merged from all docs)
    profile.extracted_nationality = merged.get("nationality", "") or ""
    profile.extracted_present_employer = merged.get("present_employer", "") or ""
    profile.extracted_marital_status = merged.get("marital_status", "") or ""
    profile.extracted_place_of_birth = merged.get("place_of_birth", "") or ""
    profile.extracted_qualification_academic = merged.get("qualification_academic", "") or ""
    profile.extracted_qualification_professional = merged.get("qualification_professional", "") or ""
    profile.extracted_lang_arabic = bool(merged.get("lang_arabic", False))
    profile.extracted_lang_english = bool(merged.get("lang_english", False))
    profile.extracted_lang_others = merged.get("lang_others", "") or ""
    profile.extracted_driving_license = merged.get("driving_license", "none") or "none"

    for attr, key in [
        ("extracted_experience_local_years", "experience_local_years"),
        ("extracted_experience_overseas_years", "experience_overseas_years"),
    ]:
        val = merged.get(key)
        if val is not None:
            try:
                setattr(profile, attr, float(val))
            except (ValueError, TypeError):
                pass

    dob_str = merged.get("date_of_birth")
    if dob_str:
        try:
            profile.extracted_dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            pass

    profile.save()
    return profile


def _job_requirements_for(candidate):
    """Build a job-requirements string from the candidate's linked recruitment."""
    rec = candidate.recruitment_id
    if rec:
        return f"{rec.job_position_id or ''} {rec.title or ''} {getattr(rec, 'description', '') or ''}".strip()
    return str(candidate.job_position_id or "")


def trigger_screening_async(candidate_id):
    """
    Run screen_candidate_cv() in a daemon thread, building the job requirements
    from the candidate's linked recruitment. Safe to call from request handlers —
    falls back through Groq → OpenRouter → regex, so it never requires an API key.
    """
    import threading

    def _run():
        try:
            candidate = Candidate.objects.select_related(
                "recruitment_id", "job_position_id"
            ).get(pk=candidate_id)
            screen_candidate_cv(candidate_id, _job_requirements_for(candidate))
        except Exception as exc:  # pragma: no cover - best effort
            print(f"[CV Screening] trigger_screening_async failed: {exc}")

    threading.Thread(target=_run, daemon=True).start()
