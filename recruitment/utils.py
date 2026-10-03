from PyPDF2 import PdfReader

def extract_resume_text(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    except Exception as e:
        print("RESUME PARSE ERROR:", e)

    return text.strip()


def build_candidate_text(app):
    resume_text = ""

    if app.get("resume_path"):
        resume_text = extract_resume_text(app["resume_path"])

    if not resume_text:
        resume_text = "No resume content found"

    return f"""
================ RESUME (70%) ================
{resume_text}

================ APPLICATION (30%) ================
Name: {app['name']}
Experience: {app.get('experience')}
Why Apply: {app.get('why_apply')}
Country: {app.get('country')}
"""