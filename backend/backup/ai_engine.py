import os
import groq
import json
import requests


def get_prompt(resume_text: str, job_description: str) -> str:
    """Generate the prompt for resume tailoring."""
    return f"""
    Tailor this Resume for the Job Description.
    Return the response as a JSON object with the following keys:
    - "name": Full name.
    - "email": Email (if available, otherwise empty string).
    - "phone": Phone (if available, otherwise empty string).
    - "linkedin": LinkedIn profile link (if available, otherwise empty string).
    - "github": GitHub profile link or handle (if available, otherwise empty string).
    - "website": Personal portfolio or website URL (if available, otherwise empty string).
    - "summary": Rewritten summary based on the job description with 3-4 sentences.
    - "experience": List of all work experiences (don't skip any job). Each object must have "company", "role", "location", "duration", "responsibilities" (list of strings with EXACTLY 20-35 words each. Each responsibility must include: action verb + specific task + measurable result/impact), and "skills" (list of strings of technologies used in this job).
    - "education": List of all education details (unchanged). Each object must have "institution", "degree", "location", and "duration".
    - "certifications": List of relevant certifications (if available, otherwise empty list). Include only certifications that align with the job description. Each string should include certification name and issuing organization if available, formatted like "Certification Name, Issuing Organization".
    - "trainings": List of relevant trainings (if available, otherwise empty list). Include only trainings that align with the job description. Each string should include training name and issuing organization if available, formatted like "Training Name, Issuing Organization".
    - "skills": List of relevant 15 skills.
    - "projects": List of projects. Choose at most 3 most relevant projects. Each object must have "name", "description", and "skills" (list of strings of specific tools, languages, and technologies used in this project).
    - "languages": List of languages spoken/written (if available, otherwise empty list). Each object must have "name" and "proficiency".
    
    Rules:
    - No hallucinations. Use only provided info. Don't lie.
    - Match JD keywords naturally.
    - No intro/outro text. ONLY JSON.

    Resume: {resume_text}
    JD: {job_description}
    """


def tailor_resume_with_groq(resume_text: str, job_description: str) -> dict:
    """Tailor resume using Groq API."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
        
    client = groq.Groq(api_key=api_key)
    prompt = get_prompt(resume_text, job_description)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional resume writer. You must return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=os.environ.get("GROQ_MODEL", "mixtral-8x7b-32768"),
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    try:
        content = chat_completion.choices[0].message.content
        return json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Error parsing AI response: {e}")
        return _get_error_response(content)


def tailor_resume_with_ollama(resume_text: str, job_description: str) -> dict:
    """Tailor resume using local Ollama model."""
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL", "mistral")
    
    prompt = get_prompt(resume_text, job_description)

    try:
        response = requests.post(
            f"{ollama_host}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "temperature": 0.3,
            },
            timeout=120
        )
        response.raise_for_status()
        
        result = response.json()
        content = result.get("response", "")
        
        return json.loads(content)
    except requests.exceptions.ConnectionError:
        raise ValueError(
            f"Cannot connect to Ollama at {ollama_host}. Make sure Ollama is running.\n"
            f"Start it with: ollama serve\n"
            f"Pull a model with: ollama pull {model}"
        )
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Error parsing AI response: {e}")
        return _get_error_response(content)


def _get_error_response(content: str) -> dict:
    """Return error response structure."""
    return {
        "name": "Parsed Error",
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": "",
        "website": "",
        "summary": "There was an error parsing the AI response.",
        "experience": content,
        "education": "",
        "certifications": [],
        "trainings": [],
        "skills": "",
        "projects": "",
        "languages": []
    }


def tailor_resume(resume_text: str, job_description: str) -> dict:
    """Main function - routes to appropriate provider based on LLM_PROVIDER env var."""
    provider = os.environ.get("LLM_PROVIDER", "groq").lower()
    
    if provider == "ollama":
        return tailor_resume_with_ollama(resume_text, job_description)
    elif provider == "groq":
        return tailor_resume_with_groq(resume_text, job_description)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Use 'groq' or 'ollama'.")
