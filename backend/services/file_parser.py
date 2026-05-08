import PyPDF2
from werkzeug.datastructures import FileStorage

def parse_file(file: FileStorage) -> str:
    filename = file.filename.lower()
    
    if filename.endswith('.txt'):
        return file.read().decode('utf-8', errors='ignore')
        
    elif filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
        
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or TXT file.")
