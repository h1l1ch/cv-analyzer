import os
import json
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from openai import OpenAI
import PyPDF2
from .forms import CVUploadForm
from .models import CVAnalysis
from django.contrib.auth.decorators import login_required

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def create_admin(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    return HttpResponse("Admin created")

def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        return text.strip()
    except Exception:
        return ""


def debug_templates(request):
    return HttpResponse(str(settings.TEMPLATES))


@login_required
def home(request):
    if request.method == "POST":
        form = CVUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data.get("file")
            text_input = request.POST.get("cv_text")
            job_description = form.cleaned_data.get("job_description")

            text = ""

            # 📄 If PDF uploaded → use it
            if file:
                if not file.name.endswith(".pdf"):
                    return HttpResponse("Only PDF files are allowed.")

                text = extract_text_from_pdf(file)

            # 📝 If text pasted → use it
            elif text_input and text_input.strip():
                text = text_input

            else:
                return HttpResponse("Please upload a PDF or paste CV text.")

            if not text.strip():
                return HttpResponse("No text provided.")

            # 🧠 AI prompt
            prompt = f"""
You are an expert recruiter.

Analyze how well this CV matches the job description.

Return ONLY valid JSON:

{{
  "match_score": 0-100,
  "strengths": [],
  "missing_skills": [],
  "improvements": [],
  "summary": ""
}}

CV:
{text}

JOB DESCRIPTION:
{job_description}
"""

            try:
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt
                )

                result_text = response.output[0].content[0].text.strip()

                # Clean markdown
                if result_text.startswith("```"):
                    parts = result_text.split("```")
                    if len(parts) >= 2:
                        result_text = parts[1]
                    if result_text.startswith("json"):
                        result_text = result_text[4:]
                    result_text = result_text.strip()

                data = json.loads(result_text)

                CVAnalysis.objects.create(
                    user=request.user,
                    match_score=data.get("match_score", 0),
                    summary=data.get("summary", "")
                )

                return render(request, "analyzer/result.html", {"data": data})

            except Exception as e:
                return HttpResponse(f"<pre>Error: {e}</pre>")

    else:
        form = CVUploadForm()

    return render(request, "analyzer/home.html", {"form": form})

@login_required
def dashboard(request):
    analyses = CVAnalysis.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "analyzer/dashboard.html", {"analyses": analyses})