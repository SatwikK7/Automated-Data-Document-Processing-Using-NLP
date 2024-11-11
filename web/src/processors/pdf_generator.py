from fpdf import FPDF

class PDFGenerator:
    def create_summary_pdf(self, summary: str, original_filename: str) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        
        # Add title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Summary of {original_filename}", ln=True, align="C")
        
        # Add summary content
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, summary)
        
        return pdf.output(dest="S").encode("latin1")