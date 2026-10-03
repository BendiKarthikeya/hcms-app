from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def screen_candidate(jd, candidate_text):
    prompt = f"""
You are a senior technical recruiter conducting a thorough candidate evaluation.

Scoring weights (apply strictly):
- 70% Resume: relevance of experience, seniority, company calibre (FAANG/big tech/tier-1 startups = strong positive), educational institution tier, certifications, project depth
- 30% Application answers: quality, clarity, honesty, role-specific insight

Positive signals to note explicitly if present:
- Experience at well-known companies (FAANG, Fortune 500, top-tier startups)
- Degree from a recognised/top-ranked university
- Years of directly relevant experience
- Leadership, founding, or ownership roles
- Certifications or advanced degrees relevant to the role
- Strong, specific answers that show genuine understanding of the role

Negative signals to note explicitly if present:
- Missing required fields in the application (e.g. country, experience)
- Vague or one-line answers that show no effort
- No relevant technical experience for a technical role
- Significant gaps or irrelevant career trajectory
- Degree from an unknown institution with no compensating experience

JOB DESCRIPTION:
{jd}

CANDIDATE DATA:
{candidate_text}

Return ONLY valid JSON in exactly this format:
{{
  "score": <number 0-100>,
  "decision": "select" or "reject",
  "reason": "One concise paragraph summarising the overall assessment.\\n\\nSTRENGTHS:\\n- <point>\\n- <point>\\n\\nWEAKNESSES:\\n- <point>\\n- <point>"
}}

The reason field MUST contain: a short opening paragraph, then a STRENGTHS section with bullet points, then a WEAKNESSES section with bullet points. Be specific — name companies, universities, skills, or missing fields directly.
"""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    return res.choices[0].message.content


def rank_top_candidates(jd, candidates, target_count):
    """
    Second-pass ranking: pick the best target_count candidates from a pre-screened list.
    candidates: list of dicts {id, name, score, reason}
    Returns: list of IDs to keep.
    Falls back to score-based sort on AI failure.
    """
    import json as _json, re as _re

    candidates_text = "\n---\n".join([
        f"[ID:{c['id']}] {c['name']} | Score: {c['score']}/100\nReasoning: {c['reason']}"
        for c in candidates
    ])

    prompt = f"""You are an AI recruiter performing a second-round shortlisting.

Select the BEST {target_count} candidates for interview from the list below.
Weigh their score, AI reasoning, and overall fit for the role.

JOB DESCRIPTION:
{jd}

CANDIDATES:
{candidates_text}

Return ONLY valid JSON — an array of the {target_count} best candidate IDs:
{{"selected_ids": [1, 2, 3, ...]}}
"""

    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        raw = res.choices[0].message.content
        match = _re.search(r'\{.*\}', raw, _re.DOTALL)
        data = _json.loads(match.group())
        return [int(i) for i in data["selected_ids"]][:target_count]
    except Exception:
        sorted_by_score = sorted(candidates, key=lambda c: c.get("score", 0), reverse=True)
        return [c["id"] for c in sorted_by_score[:target_count]]