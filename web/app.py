# app.py
import streamlit as st
from src.processors.document_processor import DocumentProcessor
from src.processors.pdf_generator import PDFGenerator
from src.processors.ollama_service import OllamaService

def main():
    st.title("Document Analysis Tool")
    
    # Initialize services
    doc_processor = DocumentProcessor()
    pdf_generator = PDFGenerator()
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
        st.session_state.current_summary = None  # Reset summary when new file is uploaded
    
    # File upload section
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader("Upload a file", type=["xml", "json", "pdf", "txt"])
    if uploaded_file:
        process_uploaded_file(uploaded_file)
    
    # Display processed content and actions
    if st.session_state.processed_content:
        st.subheader("Document Analysis")
        
        # Create two columns for summary and PDF download
        col1, col2 = st.columns([3, 1])
        
        # Summary Generation
        with col1:
            if st.button("Generate Summary"):
                with st.spinner("Generating summary..."):
                    if isinstance(st.session_state.processed_content, dict):
                        content_for_summary = str(st.session_state.processed_content.get("content", str(st.session_state.processed_content)))
                    else:
                        content_for_summary = str(st.session_state.processed_content)
                    
                    summary = ollama_service.generate_summary(content_for_summary, "document")
                    st.session_state.current_summary = summary
                    st.text_area("Summary", summary, height=200)
        
        # PDF Download
        with col2:
            if st.session_state.current_summary:
                try:
                    pdf_bytes = pdf_generator.create_summary_pdf(st.session_state.current_summary, "document_summary")
                    st.download_button(
                        label="Download Summary PDF",
                        data=pdf_bytes,
                        file_name="document_summary.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error("Error generating PDF. Please try again.")
        
        # Document Querying - Always visible after file upload
        st.subheader("Ask Questions About the Document")
        user_query = st.text_input("Enter your question:")
        if user_query:  # Remove the button to make it more responsive
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