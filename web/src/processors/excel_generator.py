import xml.etree.ElementTree as ET
from openpyxl import Workbook
import json
import io

class ExcelGenerator:
    def __init__(self):
        self.workbook = None

    def flatten_element(self, element, parent_data):
        """Recursively flatten XML elements into a single dictionary."""
        row_data = parent_data.copy()

        # Add attributes
        for attr, value in element.attrib.items():
            row_data[f"{element.tag} {attr}"] = value

        # Add text content
        if element.text and element.text.strip():
            row_data[element.tag] = element.text.strip()

        # Process children
        if len(element):
            for child in element:
                row_data = self.flatten_element(child, row_data)

        return row_data

    def flatten_json(self, json_obj, parent_key='', sep='_'):
        """Recursively flatten JSON object into a single dictionary."""
        items = []
        for key, value in json_obj.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key

            if isinstance(value, dict):
                items.extend(self.flatten_json(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        items.extend(self.flatten_json(item, f"{new_key}{sep}{i}", sep=sep).items())
                    else:
                        items.append((f"{new_key}{sep}{i}", str(item)))
            else:
                items.append((new_key, str(value)))
        return dict(items)

    def process_xml_content(self, content: bytes) -> bytes:
        """Process XML content and convert to Excel."""
        try:
            # Parse XML from bytes
            root = ET.fromstring(content)
            
            # Prepare data structures
            rows = []
            headers = set()

            # Flatten each top-level element
            for element in root:
                row = self.flatten_element(element, {})
                rows.append(row)
                headers.update(row.keys())

            # Create workbook and process data
            wb = Workbook()
            sheet = wb.active
            headers = sorted(headers)
            
            # Write headers
            sheet.append(headers)
            
            # Write data rows
            for row in rows:
                sheet.append([row.get(header, "") for header in headers])

            # Save to bytes
            excel_buffer = io.BytesIO()
            wb.save(excel_buffer)
            excel_buffer.seek(0)
            
            return excel_buffer.getvalue()

        except Exception as e:
            raise Exception(f"Error processing XML: {str(e)}")

    def process_json_content(self, content: bytes) -> bytes:
        """Process JSON content and convert to Excel."""
        try:
            # Parse JSON from bytes
            json_data = json.loads(content)
            
            # Handle both single object and list of objects
            if isinstance(json_data, dict):
                json_data = [json_data]
            
            # Flatten each object
            rows = []
            headers = set()
            
            for item in json_data:
                flattened = self.flatten_json(item)
                rows.append(flattened)
                headers.update(flattened.keys())
            
            # Create workbook and process data
            wb = Workbook()
            sheet = wb.active
            headers = sorted(headers)
            
            # Write headers
            sheet.append(headers)
            
            # Write data rows
            for row in rows:
                sheet.append([row.get(header, "") for header in headers])

            # Save to bytes
            excel_buffer = io.BytesIO()
            wb.save(excel_buffer)
            excel_buffer.seek(0)
            
            return excel_buffer.getvalue()

        except Exception as e:
            raise Exception(f"Error processing JSON: {str(e)}")

    def create_excel(self, content: bytes, file_type: str) -> bytes:
        """
        Create Excel file based on input content type
        
        Args:
            content (bytes): The file content
            file_type (str): The mime type of the file
            
        Returns:
            bytes: The Excel file as bytes
        """
        try:
            if "xml" in file_type.lower():
                return self.process_xml_content(content)
            elif "json" in file_type.lower():
                return self.process_json_content(content)
            else:
                raise ValueError("Unsupported file type for Excel conversion")
                
        except Exception as e:
            # Create error workbook
            error_wb = Workbook()
            error_sheet = error_wb.active
            error_sheet['A1'] = "Error Creating Excel File"
            error_sheet['A2'] = str(e)
            
            error_buffer = io.BytesIO()
            error_wb.save(error_buffer)
            error_buffer.seek(0)
            
            return error_buffer.getvalue()