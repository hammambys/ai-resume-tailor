from flask import Blueprint, request, jsonify
from services.file_parser import parse_file
from services.text_cleaner import clean_text
from services.ai_engine import tailor_resume

resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/tailor', methods=['POST'])
def tailor():
    # ... (existing code)
    try:
        if 'resume_file' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        resume_file = request.files['resume_file']
        job_description = request.form.get('job_description')

        if not resume_file.filename:
            return jsonify({'error': 'Empty file provided'}), 400
            
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400

        raw_text = parse_file(resume_file)
        if not raw_text:
            return jsonify({'error': 'Could not extract text from the file'}), 400

        cleaned_text = clean_text(raw_text)
        tailored_resume = tailor_resume(cleaned_text, job_description)

        return jsonify({
            'success': True,
            'original_length': len(cleaned_text),
            'tailored_resume': tailored_resume
        })

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': 'An internal error occurred during processing.'}), 500
