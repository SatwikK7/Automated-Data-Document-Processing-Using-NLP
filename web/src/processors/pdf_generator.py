# pdf_generator.py
from fpdf import FPDF
import re

class PDFGenerator:
    def __init__(self):
        self.pdf = FPDF()
        # Add Unicode font support
        self.pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        
    def clean_text(self, text: str) -> str:
        """Clean text to remove problematic characters"""
        # Replace problematic characters with their closest ASCII equivalents
        replacements = {
            '€': 'EUR',
            '—': '-',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '…': '...',
            '–': '-'
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
            
        # Remove any remaining non-ASCII characters
        text = text.encode('ascii', 'ignore').decode()
        return text
        
    def create_summary_pdf(self, summary: str, original_filename: str) -> bytes:
        try:
            # Create new PDF object for each call
            pdf = FPDF()
            pdf.add_page()
            
            # Set font to Arial which supports basic characters
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, f"Summary of {original_filename}", ln=True, align="C")
            
            # Set font for main content
            pdf.set_font("Arial", "", 12)
            
            # Clean and process the summary text
            cleaned_summary = self.clean_text(summary)
            
            # Split text into lines to avoid overflow
            lines = cleaned_summary.split('\n')
            for line in lines:
                # Further split long lines
                words = line.split()
                current_line = ''
                for word in words:
                    # Test if adding the word exceeds line width
                    test_line = current_line + ' ' + word if current_line else word
                    if pdf.get_string_width(test_line) < 180:  # Adjust width as needed
                        current_line = test_line
                    else:
                        pdf.multi_cell(0, 10, current_line)
                        current_line = word
                if current_line:
                    pdf.multi_cell(0, 10, current_line)
                    
            # Return PDF as bytes
            return pdf.output(dest='S').encode('latin-1', errors='replace')
            
        except Exception as e:
            # If PDF generation fails, return a simple PDF with error message
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Error Creating PDF", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 10, "Could not generate PDF with special characters. Please try again.")
            return pdf.output(dest='S').encode('latin-1', errors='replace')