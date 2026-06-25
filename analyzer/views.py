from django.shortcuts import render
from .forms import ResumeForm
from PyPDF2 import PdfReader

job_roles = {
     "Python Developer": [
        "Python", "Django", "Flask", "SQL",
        "Git", "REST API", "OOP", "Pandas"
    ],

    "Java Developer": [
        "Java", "Spring Boot", "Hibernate",
        "MySQL", "Maven", "Git", "JPA"
    ],

    "Full Stack Developer": [
        "HTML", "CSS", "JavaScript",
        "React", "Node.js", "MongoDB",
        "Express.js", "Git"
    ],

    "Frontend Developer": [
        "HTML", "CSS", "JavaScript",
        "React", "Bootstrap", "TypeScript"
    ],

    "Backend Developer": [
        "Python", "Django", "Node.js",
        "REST API", "SQL", "Git"
    ],

    "Data Analyst": [
        "Python", "SQL", "Excel",
        "Power BI", "Tableau", "Statistics"
    ],

    "Data Scientist": [
        "Python", "Machine Learning",
        "Pandas", "NumPy", "TensorFlow",
        "Scikit-learn", "SQL"
    ],

    "Machine Learning Engineer": [
        "Python", "TensorFlow",
        "PyTorch", "Deep Learning",
        "Docker", "SQL"
    ],

    "AI Engineer": [
        "Python", "Machine Learning",
        "Deep Learning", "NLP",
        "TensorFlow", "PyTorch"
    ],

    "DevOps Engineer": [
        "Linux", "Docker",
        "Kubernetes", "AWS",
        "Jenkins", "Git"
    ],

    "Cloud Engineer": [
        "AWS", "Azure",
        "Docker", "Kubernetes",
        "Linux", "Terraform"
    ],

    "Cyber Security Analyst": [
        "Networking", "Linux",
        "Python", "Wireshark",
        "Penetration Testing"
    ],

    "Software Tester": [
        "Java", "Selenium",
        "JUnit", "Automation Testing",
        "SQL", "TestNG"
    ],

    "Android Developer": [
        "Java", "Kotlin",
        "Android Studio",
        "Firebase", "SQLite"
    ],

    "UI/UX Designer": [
        "Figma", "Adobe XD",
        "Wireframing", "Prototyping",
        "User Research"
    ]

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