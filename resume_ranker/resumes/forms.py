<form method="POST" enctype="multipart/form-data" class="card p-4 mb-4">

    {% csrf_token %}

    <label class="form-label"><strong>Select Job Role:</strong></label>

    <select name="job_role" class="form-select mb-3">
        <option value="Python Developer">Python Developer</option>
        <option value="Java Developer">Java Developer</option>
        <option value="Full Stack Developer">Full Stack Developer</option>
        <option value="Frontend Developer">Frontend Developer</option>
        <option value="Backend Developer">Backend Developer</option>
        <option value="Data Analyst">Data Analyst</option>
        <option value="Data Scientist">Data Scientist</option>
        <option value="Machine Learning Engineer">Machine Learning Engineer</option>
        <option value="AI Engineer">AI Engineer</option>
        <option value="DevOps Engineer">DevOps Engineer</option>
        <option value="Cloud Engineer">Cloud Engineer</option>
        <option value="Cyber Security Analyst">Cyber Security Analyst</option>
        <option value="Software Tester">Software Tester</option>
        <option value="Android Developer">Android Developer</option>
        <option value="UI/UX Designer">UI/UX Designer</option>
    </select>

    <label class="form-label"><strong>Candidate Name</strong></label>
    {{ form.name }}

    <br><br>

    <label class="form-label"><strong>Upload Resume (PDF)</strong></label>
    {{ form.file }}

    <br><br>

    <button type="submit" class="btn btn-primary w-100">
        Upload Resume
    </button>

</form>