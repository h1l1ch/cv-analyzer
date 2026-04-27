import os
from django.http import HttpResponse
from openai import OpenAI
from django.shortcuts import render

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  

def home(request):
    result = ""

    if request.method == "POST":
        cv_text = request.POST.get("cv_text")

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"""
            Analyze this CV and respond in this format:

            Strengths:
            - ...

            Weaknesses:
            - ...

            Suggestions:
            - ...

            CV:
            {cv_text}
            """
        )

        result = response.output[0].content[0].text

    return render(request, "analyzer/home.html", {"result": result})