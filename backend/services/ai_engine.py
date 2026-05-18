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
    - "contact": Contact information (email, phone, LinkedIn, etc.).
    - "summary": Rewritten summary based on the job description with 2-3 sentences.
    - "experience": List of all work experiences. Each object must have "company", "role", "location", "duration", "responsibilities" (list of strings with 15-25 words each with action verbs and quantify achievements where possible), and "skills" (list of strings of specific skills and technologies used in this job).
    - "education": List of all education details. Each object must have "institution", "degree", "location", and "duration".
    - "skills": List of relevant 15 skills.
    - "projects": List of projects. Choose at most 3 most relevant projects. Each object must have "name", "description" (15-25 words), and "skills" (list of strings of specific tools, languages, and technologies used in this project).

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
            "contact": "",
            "summary": "There was an error parsing the AI response.",
            "experience": content,
            "education": "",
            "skills": "",
            "projects": ""
        }
