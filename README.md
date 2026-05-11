AI CV Analyzer 🚀

Live Demo: https://cv-analyzer-zpmx.onrender.com/

Overview

AI CV Analyzer is a full-stack Django web application that uses the OpenAI API to analyze CVs and compare them against job descriptions.

Users can:

Upload CVs in PDF format
Paste CV text manually
Paste job descriptions
Receive AI-powered recruiter feedback
Get ATS-style match scores
View strengths, missing skills, and improvement suggestions

The project is deployed publicly on Render and built with production-oriented backend architecture.

Features
PDF CV Upload
AI-Powered CV Analysis
Job Description Matching
Match Score System
Strengths & Weakness Detection
ATS-Style Feedback
Authentication System
User Dashboard
Persistent Analysis Storage
Django Admin Panel
Render Deployment
Technologies Used
Backend
Python
Django
Django ORM
OpenAI API
Database
SQLite (development)
PostgreSQL-ready architecture
Frontend
HTML
CSS
Deployment
Render
Gunicorn
Whitenoise
Example Workflow
Upload a CV PDF or paste CV text
Paste a job description
AI analyzes compatibility
Receive:
Match score
Strengths
Missing skills
Improvements
Recruiter-style summary
Installation

Clone repository:

git clone https://github.com/YOUR_USERNAME/ai-cv-analyzer.git
cd ai-cv-analyzer

Create virtual environment:

python -m venv venv

Activate virtual environment:

Windows
venv\Scripts\activate
Mac/Linux
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Run migrations:

python manage.py migrate

Start server:

python manage.py runserver
Environment Variables

Create a .env file and add:

OPENAI_API_KEY=your_openai_api_key
Future Improvements
CV rewriting with AI
PDF report export
Drag & drop uploads
Advanced dashboard analytics
Better ATS scoring
Tailwind UI redesign
Multi-language support
Author

Philip Chislou

Junior Backend Python Developer focused on:

Django
AI integrations
Backend architecture
API development
Production-ready web applications
