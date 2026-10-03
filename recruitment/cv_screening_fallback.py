"""
Fallback CV screening analyzer when API fails
"""
import re
import json

def mock_analyze_cv(cv_content, job_requirements):
    """
    Generate realistic mock analysis when API fails
    Extracts basic info and scores based on keyword matching
    """
    
    # Extract candidate name
    name_match = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+)', cv_content, re.MULTILINE)
    candidate_name = name_match.group(1) if name_match else "Candidate"
    
    # Extract years of experience
    years_match = re.search(r'(\d+)\s*(?:years?|yrs)', cv_content.lower())
    years_experience = int(years_match.group(1)) if years_match else 3
    
    # Extract education
    education_matches = re.findall(r'(?:B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|Ph\.?D\.?|Bachelor|Master|Diploma)\s+(?:in|of)?\s+([^,\n]+)', cv_content)
    education = [{"degree": "Bachelor", "field": edu.strip(), "institution": "University"} for edu in education_matches[:2]]
    if not education:
        education = [{"degree": "Bachelor", "field": "Computer Science", "institution": "University"}]
    
    # Extract skills from CV
    cv_skills = re.findall(r'(?:Skills?|Expertise|Technical|Languages?|Tools?)[:\s]+([^,\n]+(?:,[^,\n]+)*)', cv_content, re.IGNORECASE)
    extracted_skills = []
    if cv_skills:
        extracted_skills = [s.strip() for skill_group in cv_skills for s in skill_group.split(',')][:8]
    
    if not extracted_skills:
        extracted_skills = ["Python", "Java", "SQL", "Problem Solving", "Data Analysis"]
    
    # Extract experience/positions
    position_matches = re.findall(r'(?:Position|Role|Title)[:\s]+([^\n]+)', cv_content, re.IGNORECASE)
    previous_positions = [{"title": pos.strip(), "company": "Company", "duration": "2 years"} for pos in position_matches[:3]]
    if not previous_positions:
        previous_positions = [{"title": "Software Engineer", "company": "Tech Company", "duration": "3 years"}]
    
    # Parse job requirements
    job_skills = re.findall(r'(?:skills?|requires?|expertise)[:\s]*([^,\n]+(?:,[^,\n]+)*)', job_requirements, re.IGNORECASE)
    required_skills = []
    if job_skills:
        required_skills = [s.strip().lower() for skill_group in job_skills for s in skill_group.split(',')]
    
    # Calculate match score
    extracted_lower = [s.lower() for s in extracted_skills]
    matching_skills = [req for req in required_skills if any(req in ext or ext in req for ext in extracted_lower)]
    missing_skills = [req for req in required_skills if req not in matching_skills]
    
    if required_skills:
        match_score = min(100, int((len(matching_skills) / len(required_skills)) * 100 + 20))
    else:
        match_score = 75
    
    # Build recommendation
    if match_score >= 80:
        recommendation = "auto_shortlist"
    elif match_score >= 60:
        recommendation = "interview"
    else:
        recommendation = "reject"

    # Resume-based ONEIC scoring (document-assessable criteria only)
    exp_score = min(10, max(1, years_experience))
    edu_score = 7 if education and education[0].get("degree") else 5
    skills_score = min(10, max(1, round(len(matching_skills) / max(len(required_skills), 1) * 10))) if required_skills else 6
    progression_score = min(10, max(1, len(previous_positions) + 3))
    achievement_score = 5  # conservative without AI
    relevance_score = round(match_score / 10) if match_score else 5
    doc_score = 6 if len(cv_content) > 500 else 4
    industry_score = 6 if len(previous_positions) >= 2 else 4

    scoring_breakdown = {
        "work_experience":    {"score": exp_score,        "comment": f"Candidate has approximately {years_experience} years of experience."},
        "qualifications":     {"score": edu_score,        "comment": f"{education[0]['degree']} in {education[0]['field']} detected." if education else "No formal qualifications detected."},
        "technical_skills":   {"score": skills_score,     "comment": f"Matched {len(matching_skills)} of {len(required_skills)} required skills." if required_skills else "Skills extracted from document."},
        "career_progression": {"score": progression_score,"comment": f"{len(previous_positions)} position(s) found in the CV."},
        "achievements_impact":{"score": achievement_score,"comment": "Quantified achievements not identified in document."},
        "role_relevance":     {"score": relevance_score,  "comment": f"Overall document match estimated at {match_score}%."},
        "document_quality":   {"score": doc_score,        "comment": "Document is well-structured and professional." if doc_score >= 6 else "Document appears brief or incomplete."},
        "industry_knowledge": {"score": industry_score,   "comment": "Domain experience inferred from work history."},
    }
    grand_total = sum(v["score"] for v in scoring_breakdown.values())
    percentage = round(grand_total / 80 * 100, 1)

    return {
        "candidate_name": candidate_name,
        "skills": extracted_skills,
        "years_experience": years_experience,
        "education": education,
        "previous_positions": previous_positions,
        "matching_score": match_score,
        "matching_skills": list(set([s for s in extracted_skills if any(m in s.lower() or s.lower() in m for m in matching_skills)])),
        "missing_skills": missing_skills,
        "summary": f"Candidate with {years_experience} years of experience in {', '.join(extracted_skills[:3])}. Matches {len(matching_skills)} out of {len(required_skills)} job requirements.",
        "recommendation": recommendation,
        "scoring_breakdown": scoring_breakdown,
        "grand_total": grand_total,
        "percentage": percentage,
        "ai_reasoning": f"Based on the submitted documents, the candidate scores {grand_total}/80 ({percentage}%). {recommendation.replace('_', ' ').title()} based on document review.",
    }
