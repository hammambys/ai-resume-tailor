# 📄 Product Requirements Document (PRD)
## 🧠 AI Resume Tailor

---

# 1. 🎯 Objective

Build a web application that allows users to upload a resume (PDF or TXT), paste a job description, and generate a tailored, ATS-optimized resume using AI. The system outputs a downloadable resume that aligns closely with the job requirements while strictly preserving factual accuracy.

The primary focus is **code simplicity, modular backend design, and efficient AI usage**.

---

# 2. 🚀 Core Features (MVP)

## 2.1 Resume Upload
- Accept file types:
  - PDF (.pdf)
  - TXT (.txt)
- Maximum file size: 5MB
- Extract raw text from uploaded file
- Normalize extracted text into clean format

---

## 2.2 Job Description Input
- Textarea input field
- Supports up to 10,000 characters
- Required for processing

---

## 2.3 AI Resume Tailoring Engine

### Inputs:
- Cleaned resume text
- Job description text

### Processing Pipeline:
1. Parse resume into logical sections:
   - Summary
   - Experience
   - Skills
   - Education
   - Projects (if available)

2. Analyze job description:
   - Extract required skills
   - Identify keywords
   - Identify responsibilities

3. Generate tailored resume:
   - Reorder and refine experience
   - Highlight relevant skills
   - Inject ATS keywords (without fabrication)
   - Maintain professional tone and structure

### Constraints:
- ❌ No hallucinated experience or skills
- ❌ No exaggerated claims
- ✅ Only restructure and optimize existing content

---

## 2.4 Output Display
- Render tailored resume in clean text format
- Allow user to copy full content
- Show loading and success states

---

## 2.5 Resume Download
- Export as PDF
- ATS-friendly formatting:
  - Single-column layout
  - Simple typography
  - No images or complex styling

---

# 3. 🧩 User Flow

1. Upload resume (PDF/TXT)
2. System extracts and cleans text
3. Paste job description
4. Click "Tailor Resume"
5. Backend processes request
6. AI generates optimized resume
7. Display result in UI
8. Download PDF

---

# 4. 🏗️ System Architecture

## 4.1 Frontend (React)

### Responsibilities:
- File upload interface
- Job description input
- Submit action handling
- Loading + error states
- Resume preview rendering
- Download button

### Design Principles:
- Component-based architecture
- Stateless UI where possible
- Minimal global state
- Clear separation of concerns:
  - Upload component
  - Input component
  - Result viewer component

---

## 4.2 Backend (Flask)

### Responsibilities:
- File handling (PDF/TXT upload)
- Text extraction
- AI request orchestration
- Resume processing pipeline
- PDF generation

### Modular Structure:

/app
  /routes
    resume.py
  /services
    file_parser.py
    text_cleaner.py
    ai_engine.py
    pdf_generator.py
  /utils

---

# 5. 🤖 AI Usage Optimization Strategy

## 5.1 Reduce Token Usage
- Pre-clean resume text
- Remove unnecessary formatting
- Send only relevant content

---

## 5.2 Structured Prompting
Resume:
[structured resume sections]

Job Description:
[clean job description]

---

## 5.3 Two-Step AI Pipeline
1. Extract structured resume
2. Tailor using structured format

---

## 5.4 Prompt Reuse Strategy
- Single system prompt reused across requests

---

## 5.5 Response Compression
- Bullet points only
- No explanations
- No extra commentary

---

## 5.6 Caching (Optional)
- Cache identical resume + job description pairs

---

# 6. 📐 Functional Requirements

| ID | Requirement |
|----|------------|
| FR1 | Support PDF and TXT uploads |
| FR2 | Extract and clean resume text |
| FR3 | Accept job description input |
| FR4 | Process resume using AI pipeline |
| FR5 | Display tailored resume in UI |
| FR6 | Allow PDF download |

---

# 7. ⚠️ Non-Functional Requirements

- Stateless backend
- Modular architecture
- Fast response time (<10s target)
- Secure file handling
- Graceful error handling
- Scalable design
