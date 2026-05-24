import os
import groq

import json

def tailor_resume(resume_text: str, job_description: str) -> dict:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
        
    client = groq.Groq(api_key=api_key)
    
    prompt = f"""
    Tailor this Resume for the Job Description.
    Return the response as a JSON object with the following keys:
    - "name": Full name.
    - "email": Email (if available, otherwise empty string).
    - "phone": Phone (if available, otherwise empty string).
    - "linkedin": LinkedIn profile link (if available, otherwise empty string).
    - "github": GitHub profile link or handle (if available, otherwise empty string).
    - "website": Personal portfolio or website URL (if available, otherwise empty string).
    - "summary": Rewritten summary based on the job description with 3-4 sentences.
    - "experience": List of all work experiences (don't skip any job). Each object must have "company", "role", "location", "duration", "responsibilities" (list of strings of rewritten responsibilities tailored for this job each with action verbs and quantify achievements where possible), and "skills" (list of strings of technologies used in this job).
    - "education": List of all education details (unchanged). Each object must have "institution", "degree", "location", and "duration".
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
        model=os.environ.get("GROQ_MODEL"),
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    try:
        content = chat_completion.choices[0].message.content
        return json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Error parsing AI response: {e}")
        # Fallback: wrap the raw content in a generic structure if it fails
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
            "skills": "",
            "projects": "",
            "languages": []
        }
