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
# ---------------- JOB RECOMMENDATION ----------------

def recommend_job(skills):

    best_role = ""
    best_match = 0

    for role, role_skills in job_roles.items():

        match = len(set(skills) & set(role_skills))

        if match > best_match:
            best_match = match
            best_role = role

    if best_role:
        return f"Based on your resume, the most suitable job role for you is {best_role}. Your skills strongly match this role."

    return "Unable to recommend a suitable job role."

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
    job_recommendation = ""

    if request.method == "POST":

        form = ResumeForm(request.POST, request.FILES)
        selected_role = request.POST.get("job_role")

        if form.is_valid():

            resume = form.save()

            try:
                pdf = PdfReader(resume.file.path)

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
                        job_recommendation = recommend_job(detected_skills)
                                        # -------- PYTHON ATS CALCULATION --------

                total_skills = len(role_skills)
                matched_skills = len(detected_skills)

                if total_skills > 0:
                    skill_score = (matched_skills / total_skills) * 40
                else:
                    skill_score = 0

                project_keywords = [
                    "project", "developed", "built",
                    "implemented", "application", "system"
                ]

                project_score = 15 if any(
                    word in extracted_text.lower()
                    for word in project_keywords
                ) else 0

                experience_keywords = [
                    "experience", "internship",
                    "intern", "worked"
                ]

                experience_score = 15 if any(
                    word in extracted_text.lower()
                    for word in experience_keywords
                ) else 0

                education_keywords = [
                    "b.e", "b.tech", "b.sc",
                    "mca", "college", "university"
                ]

                education_score = 10 if any(
                    word in extracted_text.lower()
                    for word in education_keywords
                ) else 0

                certification_score = 5 if (
                    "certificate" in extracted_text.lower() or
                    "certification" in extracted_text.lower()
                ) else 0

                keyword_score = min(matched_skills, 5) * 2

                format_score = 5 if len(extracted_text) > 800 else 2

                python_score = (
                    skill_score +
                    project_score +
                    experience_score +
                    education_score +
                    certification_score +
                    keyword_score +
                    format_score
                )
                        
                        

                # -------- ATS SCORE --------
                                # -------- ATS SCORE --------
                try:
                    ats_prompt = f"""
You are an expert Applicant Tracking System (ATS).

Analyze this resume for the role:
{selected_role}

Resume:
{extracted_text}

Evaluate based on:

1. Skills Match (40)
2. Projects (15)
3. Experience (15)
4. Education (10)
5. Certifications (5)
6. ATS Keywords (10)
7. Resume Formatting (5)

Scoring:
90-100 = Excellent
75-89 = Very Good
60-74 = Good
40-59 = Average
0-39 = Poor

Be strict.

Return ONLY one integer.

Example:
88
"""

                    ats_response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=ats_prompt
                    )

                    import re

                    numbers = re.findall(r"\d+", ats_response.text)

                    if numbers:
                        ats_score = int(numbers[0])
                    else:
                        ats_score = 0

                    ats_score = max(0, min(100, ats_score))

                    simple_suggestion = ats_suggestions(ats_score)

                except Exception as e:
                    ats_score = 0
                    simple_suggestion = f"ATS Error: {e}"

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
            "job_recommendation": job_recommendation,
        },
    )