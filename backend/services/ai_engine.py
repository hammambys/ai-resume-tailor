import os
import groq

def tailor_resume(resume_text: str, job_description: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
        
    client = groq.Groq(api_key=api_key)
    
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) optimizer and professional resume writer.
    Your task is to tailor the provided Resume to match the provided Job Description.

    Constraints:
    - DO NOT hallucinate or fabricate any experience, skills, or education.
    - ONLY reorder, refine, and optimize the existing content to highlight relevance.
    - Inject relevant keywords from the job description naturally, provided the applicant actually possesses those skills based on the original resume.
    - Keep the output professional and well-structured.
    - Use Markdown format with clear headings (e.g., Summary, Experience, Skills, Education).
    - Use bullet points for experience. Keep descriptions concise and impactful.

    Original Resume:
    {resume_text}

    Job Description:
    {job_description}

    Tailored Resume (Markdown format):
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=os.environ.get("GROQ_MODEL"),
        temperature=0.3, # Low temperature for more factual/focused responses
    )

    return chat_completion.choices[0].message.content
