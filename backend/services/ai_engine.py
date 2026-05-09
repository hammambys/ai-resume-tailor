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
    - "summary": A professional summary.
    - "experience": Work experience details in Markdown bullet points.
    - "education": Education details.
    - "skills": List of relevant skills.

    Rules:
    - No hallucinations. Use only provided info.
    - Match JD keywords naturally.
    - Use Markdown for formatting within the fields (e.g., bullet points for experience).
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
            "skills": ""
        }
