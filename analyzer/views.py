from django.shortcuts import render
from .forms import ResumeForm
from PyPDF2 import PdfReader

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ---------------- JOB ROLES ----------------
job_roles = {
    "Python Developer": ["Python", "Django", "Flask", "SQL", "Git", "REST API", "OOP", "Pandas"],
    "Java Developer": ["Java", "Spring Boot", "Hibernate", "MySQL", "Maven", "Git", "JPA"],
    "Full Stack Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "MongoDB", "Express.js", "Git"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "Bootstrap", "TypeScript"],
    "Backend Developer": ["Python", "Django", "Node.js", "REST API", "SQL", "Git"],
    "Data Analyst": ["Python", "SQL", "Excel", "Power BI", "Tableau", "Statistics"],
    "Data Scientist": ["Python", "Machine Learning", "Pandas", "NumPy", "TensorFlow", "Scikit-learn", "SQL"],
    "Machine Learning Engineer": ["Python", "TensorFlow", "PyTorch", "Deep Learning", "Docker", "SQL"],
    "AI Engineer": ["Python", "Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch"],
    "DevOps Engineer": ["Linux", "Docker", "Kubernetes", "AWS", "Jenkins", "Git"],
    "Cloud Engineer": ["AWS", "Azure", "Docker", "Kubernetes", "Linux", "Terraform"],
    "Cyber Security Analyst": ["Networking", "Linux", "Python", "Wireshark", "Penetration Testing"],
    "Software Tester": ["Java", "Selenium", "JUnit", "Automation Testing", "SQL", "TestNG"],
    "Android Developer": ["Java", "Kotlin", "Android Studio", "Firebase", "SQLite"],
    "UI/UX Designer": ["Figma", "Adobe XD", "Wireframing", "Prototyping", "User Research"]
}

# ---------------- ATS FUNCTION ----------------
def ats_suggestions(score):
    if score < 50:
        return "⚠️ Improve resume: Add skills, projects, keywords"
    elif score < 75:
        return "👍 Good resume, but improve more"
    else:
        return "🔥 Excellent resume!"


# ---------------- MAIN VIEW ----------------
def upload_resume(request):

    form = ResumeForm()
    message = ""
    extracted_text = ""
    detected_skills = []
    missing_skills = []
    ats_score = 0
    selected_role = ""
    ai_suggestion = ""
    simple_suggestion = ""

    if request.method == "POST":

        form = ResumeForm(request.POST, request.FILES)
        selected_role = request.POST.get("job_role")

        if form.is_valid():

            resume = form.save()

            try:
                pdf = PdfReader(resume.resume_file.path)

                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"

                role_skills = job_roles.get(selected_role, [])

                # -------- SKILL DETECTION --------
                for skill in role_skills:
                    if skill.lower() in extracted_text.lower():
                        detected_skills.append(skill)

                for skill in role_skills:
                    if skill not in detected_skills:
                        missing_skills.append(skill)

                # -------- ATS SCORE --------
                try:
                    ats_prompt = f"""
You are an ATS system.

Resume:
{extracted_text}

Return ONLY a number between 0 and 100.
"""

                    ats_response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=ats_prompt
                    )

                    ats_score = int(''.join(filter(str.isdigit, ats_response.text)))

                    simple_suggestion = ats_suggestions(ats_score)

                except Exception as e:
                    ats_score = 0
                    simple_suggestion = "Unable to generate suggestion"

                # -------- AI REVIEW --------
                try:
                    suggestion_prompt = f"""
You are a resume expert.

Analyze this resume:

{extracted_text}

Give:
- Strengths
- Weaknesses
- Missing Skills
"""

                    suggestion_response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=suggestion_prompt
                    )

                    ai_suggestion = suggestion_response.text

                except Exception as e:
                    ai_suggestion = f"AI Error: {e}"

                message = "Resume Uploaded Successfully"

            except Exception as e:
                message = f"Error Reading PDF: {e}"

    return render(
        request,
        "upload.html",
        {
            "form": form,
            "message": message,
            "text": extracted_text,
            "skills": detected_skills,
            "missing_skills": missing_skills,
            "ats_score": ats_score,
            "selected_role": selected_role,
            "ai_suggestion": ai_suggestion,
            "simple_suggestion": simple_suggestion,
        },
    )