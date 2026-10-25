from flask import Blueprint, request, jsonify
from services.file_parser import parse_file
from services.google_docs import GoogleDocsError, fetch_google_doc_text
from services.text_cleaner import clean_text
from services.ai_engine import tailor_resume

resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/tailor', methods=['POST'])
def tailor():
    # ... (existing code)
    try:
        resume_file = request.files.get('resume_file')
        google_doc_url = request.form.get('google_doc_url', '').strip()
        has_resume_file = resume_file is not None and bool(resume_file.filename)

        if has_resume_file and google_doc_url:
            return jsonify({'error': 'Upload a resume file or enter a Google Docs link, not both.'}), 400

        if not has_resume_file and not google_doc_url:
            if resume_file is not None:
                return jsonify({'error': 'Empty file provided'}), 400
            return jsonify({'error': 'Upload a resume file or enter a Google Docs link.'}), 400

        job_description = request.form.get('job_description', '').strip()
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400

        raw_text = (
            fetch_google_doc_text(google_doc_url)
            if google_doc_url
            else parse_file(resume_file)
        )
        if not raw_text:
            return jsonify({'error': 'Could not extract text from the file'}), 400

        cleaned_text = clean_text(raw_text)
        tailored_resume = tailor_resume(cleaned_text, job_description)

        return jsonify({
            'success': True,
            'original_length': len(cleaned_text),
            'tailored_resume': tailored_resume
        })

    except GoogleDocsError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': 'An internal error occurred during processing.'}), 500
