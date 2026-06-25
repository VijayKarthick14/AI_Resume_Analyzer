from django.shortcuts import render
from .forms import ResumeForm
from PyPDF2 import PdfReader

job_roles = {
    "Python Developer": [
        "Python",
        "Django",
        "SQL",
        "Git",
        "REST API",
    ],
    "Data Analyst": [
        "Python",
        "SQL",
        "Excel",
        "Power BI",
        "Pandas",
    ],
    "Web Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Django",
    ],
}

def upload_resume(request):

    form = ResumeForm()
    message = ""
    extracted_text = ""
    detected_skills = []
    missing_skills = []
    ats_score = 0
    selected_role = ""

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

                for skill in role_skills:
                    if skill.lower() in extracted_text.lower():
                        detected_skills.append(skill)

                for skill in role_skills:
                    if skill not in detected_skills:
                        missing_skills.append(skill)

                if len(role_skills) > 0:
                    ats_score = int(
                        (len(detected_skills) / len(role_skills)) * 100
                    )

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
        },
    )