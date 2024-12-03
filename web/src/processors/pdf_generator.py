from fpdf import FPDF
import re

class PDFGenerator:
    def __init__(self):
        self.pdf = FPDF()
        # No need to add font in init since we create new PDF object in create_summary_pdf
        
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
            # Create new PDF object
            pdf = FPDF()
            pdf.add_page()
            
            # Set fonts - using built-in Arial font
            pdf.set_font("Arial", "B", 16)
            
            # Add title
            title = f"Summary of {original_filename}"
            pdf.cell(0, 10, title, ln=True, align="C")
            
            # Set font for main content
            pdf.set_font("Arial", "", 12)
            
            # Clean and process the summary text
            cleaned_summary = self.clean_text(summary)
            
            # Split text into lines
            lines = cleaned_summary.split('\n')
            
            # Process each line
            for line in lines:
                words = line.split()
                current_line = ''
                
                # Process words in each line
                for word in words:
                    # Test if adding the word exceeds line width
                    test_line = current_line + ' ' + word if current_line else word
                    if pdf.get_string_width(test_line) < 180:  # Page width margin
                        current_line = test_line
                    else:
                        # Write current line and start new line
                        pdf.multi_cell(0, 10, current_line)
                        current_line = word
                        
                # Write any remaining text in current line
                if current_line:
                    pdf.multi_cell(0, 10, current_line)
                    
            # Return PDF as bytes
            return pdf.output(dest='S').encode('latin-1', errors='replace')
            
        except Exception as e:
            # Create error PDF if generation fails
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Error Creating PDF", ln=True)
            pdf.set_font("Arial", "", 12)
            error_msg = "Could not generate PDF with special characters. Please try again."
            pdf.multi_cell(0, 10, error_msg)
            return pdf.output(dest='S').encode('latin-1', errors='replace')