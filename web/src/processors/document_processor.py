# document_processor.py
import xml.etree.ElementTree as ET
import json
import PyPDF2
from typing import Dict, Any, Union
import io

class DocumentProcessor:
    def process_file(self, file_content: bytes, file_type: str) -> Union[Dict, str]:
        """Process different file types and return structured content"""
        try:
            if "xml" in file_type.lower():
                return self.process_xml(file_content.decode('utf-8'))
            elif "json" in file_type.lower():
                return self.process_json(file_content.decode('utf-8'))
            elif "pdf" in file_type.lower():
                return self.process_pdf(io.BytesIO(file_content))
            else:
                # For text-based files, return as string
                return file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Try alternative encoding if UTF-8 fails
                return file_content.decode('latin-1')
            except Exception as e:
                return {"error": f"Encoding error: {str(e)}"}
    
    def process_xml(self, content: str) -> Dict[str, Any]:
        try:
            root = ET.fromstring(content)
            return {
                "content": self._xml_to_text(root),
                "structure": self._xml_to_dict(root)
            }
        except ET.ParseError as e:
            return {"error": f"XML parsing error: {str(e)}"}
    
    def _xml_to_text(self, element: ET.Element, depth: int = 0) -> str:
        """Convert XML to readable text format while preserving structure"""
        text_parts = []
        
        # Add element name and any direct text
        indent = "  " * depth
        element_text = element.text.strip() if element.text and element.text.strip() else ""
        if element_text:
            text_parts.append(f"{indent}{element.tag}: {element_text}")
        else:
            text_parts.append(f"{indent}{element.tag}")
        
        # Process children
        for child in element:
            text_parts.append(self._xml_to_text(child, depth + 1))
            
            # Add any tail text
            if child.tail and child.tail.strip():
                text_parts.append(f"{indent}{child.tail.strip()}")
        
        return "\n".join(text_parts)
    
    def _xml_to_dict(self, element: ET.Element) -> Dict:
        """Convert XML to dictionary while preserving attributes"""
        result = {
            "tag": element.tag,
            "attributes": dict(element.attrib)
        }
        
        # Handle text content
        if element.text and element.text.strip():
            result["text"] = element.text.strip()
            
        # Handle children
        children = []
        for child in element:
            children.append(self._xml_to_dict(child))
            
        if children:
            result["children"] = children
            
        return result
    
    def process_json(self, content: str) -> Dict[str, Any]:
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            return {"error": f"JSON parsing error: {str(e)}"}
    
    def process_pdf(self, file) -> str:
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            return "\n".join(page.extract_text() for page in pdf_reader.pages)
        except Exception as e:
            return f"PDF parsing error: {str(e)}"