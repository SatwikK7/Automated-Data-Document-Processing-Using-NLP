import streamlit as st
from src.processors.document_processor import DocumentProcessor
from src.processors.pdf_generator import PDFGenerator
from src.processors.ollama_service import OllamaService
from src.processors.excel_generator import ExcelGenerator

def main():
    st.title("Document Analysis Tool")
    
    # Initialize services
    doc_processor = DocumentProcessor()
    pdf_generator = PDFGenerator()
    excel_generator = ExcelGenerator()
    ollama_service = OllamaService(model_name="llama3.2")
    
    # Initialize session state
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = {}
    if 'processed_content' not in st.session_state:
        st.session_state.processed_content = None
    if 'current_summary' not in st.session_state:
        st.session_state.current_summary = None
    
    def process_uploaded_file(file):
        content = file.read()
        processed_content = doc_processor.process_file(content, file.type)
        
        if isinstance(processed_content, dict) and "error" in processed_content:
            st.error(f"Error processing file: {processed_content['error']}")
            return
        
        st.session_state.processed_files[file.name] = {
            "content": content,
            "type": file.type,
            "processed": processed_content
        }
        st.session_state.processed_content = processed_content
        st.session_state.current_summary = None
    
    # File upload section
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader("Upload a file", type=["xml", "json", "pdf", "txt"])
    
    if uploaded_file:
        process_uploaded_file(uploaded_file)
        
        # Check the uploaded file type
        if uploaded_file.name.endswith(".xml") or uploaded_file.name.endswith(".json"):
            st.subheader("Available Actions")
            
            # Excel Conversion - Immediate option for XML/JSON
            try:
                file_content = st.session_state.processed_files[uploaded_file.name]["content"]
                excel_bytes = excel_generator.create_excel(
                    file_content,
                    uploaded_file.type
                )
                
                st.download_button(
                    label="Convert to Excel",
                    data=excel_bytes,
                    file_name=f"{uploaded_file.name}_converted.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error generating Excel: {str(e)}")
            
            # Generate Summary Option
            if st.button("Generate Summary"):
                with st.spinner("Generating summary..."):
                    if isinstance(st.session_state.processed_content, dict):
                        content_for_summary = str(st.session_state.processed_content.get("content", str(st.session_state.processed_content)))
                    else:
                        content_for_summary = str(st.session_state.processed_content)
                    
                    summary = ollama_service.generate_summary(content_for_summary, "document")
                    st.session_state.current_summary = summary
            
            # Display summary if it exists
            if st.session_state.current_summary:
                st.subheader("Document Summary")
                st.text_area("Summary", st.session_state.current_summary, height=200)
            
            # Display PDF download if summary exists
            if st.session_state.current_summary:
                try:
                    pdf_bytes = pdf_generator.create_summary_pdf(st.session_state.current_summary, uploaded_file.name)
                    st.download_button(
                        label="Download Summary PDF",
                        data=pdf_bytes,
                        file_name=f"{uploaded_file.name}_summary.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error("Error generating PDF. Please try again.")
        
        else:  # For TXT and PDF files
            st.subheader("Available Actions")
            
            # Generate Summary Option
            if st.button("Generate Summary"):
                with st.spinner("Generating summary..."):
                    if isinstance(st.session_state.processed_content, dict):
                        content_for_summary = str(st.session_state.processed_content.get("content", str(st.session_state.processed_content)))
                    else:
                        content_for_summary = str(st.session_state.processed_content)
                    
                    summary = ollama_service.generate_summary(content_for_summary, "document")
                    st.session_state.current_summary = summary
            
            # Display summary if it exists
            if st.session_state.current_summary:
                st.subheader("Document Summary")
                st.text_area("Summary", st.session_state.current_summary, height=200)
            
            # Display PDF download if summary exists
            if st.session_state.current_summary:
                try:
                    pdf_bytes = pdf_generator.create_summary_pdf(st.session_state.current_summary, uploaded_file.name)
                    st.download_button(
                        label="Download Summary PDF",
                        data=pdf_bytes,
                        file_name=f"{uploaded_file.name}_summary.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error("Error generating PDF. Please try again.")
        
        # Document Querying - Always visible after file upload
        st.subheader("Ask Questions About the Document")
        user_query = st.text_input("Enter your question:")
        if user_query:
            with st.spinner("Analyzing document..."):
                if isinstance(st.session_state.processed_content, dict):
                    content_for_query = str(st.session_state.processed_content.get("content", str(st.session_state.processed_content)))
                else:
                    content_for_query = str(st.session_state.processed_content)
                    
                answer = ollama_service.query_document(content_for_query, user_query)
                st.markdown("### Answer")
                st.write(answer)

if __name__ == "__main__":
    main()
