import streamlit as st
from src.processors.document_processor import DocumentProcessor
from src.processors.pdf_generator import PDFGenerator
from src.processors.ollama_service import OllamaService
from src.processors.excel_generator import ExcelGenerator
from src.processors.smart_analysis import SmartAnalysisService
import streamlit.components.v1 as components

# Configure Streamlit theme for light mode
st.set_page_config(
    page_title="Document Analysis Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css(file_path: str):
    with open(file_path) as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)



def main():
    st.title("📊 Document Analysis Tool")
    # Initialize services
    # Call the function to load custom CSS
    load_css("C:/Users/Satwik K/Desktop/SG_Hackathon/project/web/styles/custom.css")
    doc_processor = DocumentProcessor()
    pdf_generator = PDFGenerator()
    excel_generator = ExcelGenerator()
    ollama_service = OllamaService(model_name="llama3.2")
    smart_analysis = SmartAnalysisService(ollama_service)
    
    
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
    st.subheader("📁 Upload Document")
    uploaded_file = st.file_uploader(
        "Upload a file (XML, JSON, PDF, TXT supported)",
        type=["xml", "json", "pdf", "txt"]
    )
    
    if uploaded_file:
        process_uploaded_file(uploaded_file)
        
        st.subheader("🔧 Available Actions")
        
        # Create columns for actions
        col1, col2, col3, col4 = st.columns(4)
        
        # XML/JSON specific actions
        if uploaded_file.name.endswith((".xml", ".json")):
            with col1:
                try:
                    file_content = st.session_state.processed_files[uploaded_file.name]["content"]
                    excel_bytes = excel_generator.create_excel(
                        file_content,
                        uploaded_file.type
                    )
                    
                    st.download_button(
                        label="📊 Convert to Excel",
                        data=excel_bytes,
                        file_name=f"{uploaded_file.name}_converted.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Error generating Excel: {str(e)}")
        
        # Smart Trade Analysis Button
        with col2:
            if st.button("🔍 Smart Trade Analysis"):
                try:
                    file_content = st.session_state.processed_files[uploaded_file.name]["content"]
                    # Use Ollama Service to analyze the file and determine if it's trade-related
                    analysis = ollama_service.generate_response(
                        str(file_content),
                        "Analyze the following document for trade-related content and provide smart trade analysis if applicable. If not, return an error message."
                    )
                    
                    if "error" in analysis.lower():
                        st.error(analysis)  # Display the error from Ollama response
                    else:
                        st.subheader("📈 Trade Analysis Results")
                        st.markdown(analysis)  # Display the AI-generated trade analysis result
                except Exception as e:
                    st.error(f"Error in trade analysis: {str(e)}")

        
        # Generate Summary Button
        with col3:
            if st.button("📝 Generate Summary"):
                with st.spinner("Generating summary..."):
                    if isinstance(st.session_state.processed_content, dict):
                        content_for_summary = str(st.session_state.processed_content.get("content", str(st.session_state.processed_content)))
                    else:
                        content_for_summary = str(st.session_state.processed_content)
                    
                    summary = ollama_service.generate_summary(content_for_summary, "document")
                    st.session_state.current_summary = summary
        
        # Display summary if it exists
        if st.session_state.current_summary:
            st.subheader("📋 Document Summary")
            st.text_area("Summary", st.session_state.current_summary, height=200)
            
            try:
                pdf_bytes = pdf_generator.create_summary_pdf(st.session_state.current_summary, uploaded_file.name)
                st.download_button(
                    label="📄 Download Summary PDF",
                    data=pdf_bytes,
                    file_name=f"{uploaded_file.name}_summary.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error("Error generating PDF. Please try again.")
        
        # Document Querying
        st.subheader("❓ Ask Questions About the Document")
        user_query = st.text_input("Enter your question:")
        if user_query:
            with st.spinner("Analyzing document..."):
                if isinstance(st.session_state.processed_content, dict):
                    content_for_query = str(st.session_state.processed_content.get("content", str(st.session_state.processed_content)))
                else:
                    content_for_query = str(st.session_state.processed_content)
                    
                answer = ollama_service.query_document(content_for_query, user_query)
                st.markdown("### 💡 Answer")
                st.write(answer)

if __name__ == "__main__":   
    main()
