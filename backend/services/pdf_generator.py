from fpdf import FPDF
import io

class ResumePDF(FPDF):
    def header(self):
        # No header for resume
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_pdf(markdown_text: str) -> io.BytesIO:
    pdf = ResumePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Basic support for markdown-like text
    # Since FPDF doesn't handle full markdown, we'll do some basic cleaning
    # A more advanced approach would use a library that converts MD to PDF
    
    lines = markdown_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue
            
        if line.startswith('# '):
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, line[2:], ln=True)
            pdf.ln(2)
        elif line.startswith('## '):
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, line[3:], ln=True)
            pdf.ln(1)
        elif line.startswith('### '):
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 10, line[4:], ln=True)
        elif line.startswith('- ') or line.startswith('* '):
            pdf.set_font("helvetica", "", 11)
            # Use a bullet point
            pdf.write(5, chr(149) + " ")
            pdf.write_html(line[2:])
            pdf.ln(6)
        else:
            pdf.set_font("helvetica", "", 11)
            # Handle bold within text if needed, but for simplicity:
            clean_line = line.replace('**', '').replace('__', '')
            pdf.multi_cell(0, 6, clean_line)
            pdf.ln(2)
            
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer
