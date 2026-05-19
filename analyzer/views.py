import os
import json
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.shortcuts import render
from openai import OpenAI
import PyPDF2
from .forms import CVUploadForm
from .models import CVAnalysis
from django.contrib.auth.decorators import login_required

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def download_pdf(request):
    text = request.GET.get("text", "")

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    story = []

    paragraphs = text.split("\n")

    for para in paragraphs:
        story.append(Paragraph(para, styles["BodyText"]))
        story.append(Spacer(1, 4))

    doc.build(story)

    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="improved_cv.pdf"'

    return response

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


def home(request):

    if request.method == "POST":

        print(request.POST)

        action = request.POST.get("action", "analyze")

        print("ACTION =", action)
        form = CVUploadForm(request.POST, request.FILES)

        if form.is_valid():

            file = form.cleaned_data.get("file")
            text_input = request.POST.get("text")
            job_description = form.cleaned_data.get("job_description")

            text = ""

            # 📄 PDF upload
            if file:

                if not file.name.endswith(".pdf"):
                    return HttpResponse("Only PDF files are allowed.")

                text = extract_text_from_pdf(file)

            # 📝 Pasted text
            elif text_input and text_input.strip():

                text = text_input

            else:
                return HttpResponse("Please upload a PDF or paste CV text.")

            if not text.strip():
                return HttpResponse("No text provided.")

            # =========================
            # 🧠 ANALYZE CV
            # =========================

            if action == "analyze":

                prompt = f"""
You are an expert recruiter.

Analyze how well this CV matches the job description.

Return ONLY valid JSON:

- Format the output like a clean professional CV
- Use sections and bullet points

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

            # =========================
            # ✨ IMPROVE CV
            # =========================

            elif action == "improve":

                prompt = f"""
You are an expert technical recruiter and professional CV writer.

Improve this CV specifically for the provided job description.

Requirements:
- Make the CV stronger and more professional
- Improve wording and bullet points
- Optimize for ATS systems
- Keep information truthful
- Use strong action verbs
- Improve clarity and structure

Return ONLY the improved CV text.

CV:
{text}

JOB DESCRIPTION:
{job_description}
"""

            else:
                return HttpResponse(f"Invalid action: {action}")

            # =========================
            # 🤖 OPENAI REQUEST
            # =========================

            try:

                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt
                )

                result_text = response.output[0].content[0].text.strip()

                # Clean markdown formatting
                if result_text.startswith("```"):

                    parts = result_text.split("```")

                    if len(parts) >= 2:
                        result_text = parts[1]

                    if result_text.startswith("json"):
                        result_text = result_text[4:]

                    result_text = result_text.strip()

                # =========================
                # 📊 ANALYZE RESULT
                # =========================

                if action == "analyze":

                    data = json.loads(result_text)

                    user = (
                        request.user
                        if request.user.is_authenticated
                        else None
                    )

                    CVAnalysis.objects.create(
                        user=user,
                        match_score=data.get("match_score", 0),
                        summary=data.get("summary", ""),
                        strengths=json.dumps(data.get("strengths", [])),
                        missing_skills=json.dumps(
                            data.get("missing_skills", [])
                        ),
                        improvements=json.dumps(
                            data.get("improvements", [])
                        ),
                        cv_text=text,
                        job_description=job_description,
                    )

                    return render(
                        request,
                        "analyzer/result.html",
                        {"data": data}
                    )

                # =========================
                # ✨ IMPROVED CV RESULT
                # =========================

                elif action == "improve":

                    return render(
                        request,
                        "analyzer/improved_cv.html",
                        {"improved_cv": result_text}
                    )

            except Exception as e:

                return HttpResponse(f"<pre>Error: {e}</pre>")

    else:

        form = CVUploadForm()

    return render(
        request,
        "analyzer/home.html",
        {"form": form}
    )

@login_required
def dashboard(request):
    analyses = CVAnalysis.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "analyzer/dashboard.html", {"analyses": analyses})

@login_required
def analysis_detail(request, analysis_id):

    analysis = CVAnalysis.objects.get(
        id=analysis_id,
        user=request.user
    )

    return render(
        request,
        "analyzer/analysis_detail.html",
        {"analysis": analysis}
    )