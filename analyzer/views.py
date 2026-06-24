from django.shortcuts import render
from .forms import ResumeForm

def upload_resume(request):

    message = ""

    if request.method == 'POST':

        form = ResumeForm(request.POST, request.FILES)

        if form.is_valid():

            form.save()
            message = "Resume Uploaded Successfully"

    else:
        form = ResumeForm()

    return render(
        request,
        'upload.html',
        {
            'form': form,
            'message': message
        }
    )