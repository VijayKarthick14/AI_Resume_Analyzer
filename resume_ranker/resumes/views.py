from django.shortcuts import render
from .models import Resume
import PyPDF2

# 🔥 SKILL DATABASE
SKILL_DB = [
    "python", "django", "flask", "sql", "mysql",
    "html", "css", "javascript", "react",
    "machine learning", "ai", "deep learning",
    "aws", "docker", "git"
]

# 📄 EXTRACT TEXT
def extract_text(file_path):
    text = ""

    try:
        pdf = PyPDF2.PdfReader(open(file_path, "rb"))

        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

    except Exception as e:
        print("PDF ERROR:", e)

    return text.lower()

# 🔍 SKILL DETECTION
def detect_skills(text):
    return [skill for skill in SKILL_DB if skill in text]

# 📊 ATS SCORE
def calculate_score(skills, job_role):
    score = len(skills) * 10

    if job_role and job_role.lower().find("python") != -1:
        if "python" in skills:
            score += 20

    return min(score, 100)

# 🚀 MAIN VIEW
def upload_resume(request):
    context = {}

    if request.method == "POST":

        job_role = request.POST.get("job_role")
        files = request.FILES.getlist("file")

        results = []

        for f in files:
            resume = Resume.objects.create(name=f.name, file=f)

            # extract text
            text = extract_text(resume.file.path)

            # skills
            skills = detect_skills(text)

            # score
            score = calculate_score(skills, job_role)

            resume.score = score
            resume.save()

            results.append({
                "name": f.name,
                "skills": skills,
                "score": score,
                "text": text[:500]
            })

        # ranking
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        context = {
            "message": "Resumes analyzed successfully",
            "results": results,
            "selected_role": job_role
        }

    return render(request, "upload.html", context)