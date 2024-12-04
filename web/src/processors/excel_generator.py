import xml.etree.ElementTree as ET
from openpyxl import Workbook
import json
import io
from datetime import datetime

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

    def flatten_json_list(self, json_list):
        """Handle JSON list of objects by creating multiple rows."""
        rows = []
        headers = set()
        
        def flatten_dict(d, prefix=''):
            items = {}
            for k, v in d.items():
                new_key = f"{prefix}{k}" if prefix else k
                
                if isinstance(v, dict):
                    items.update(flatten_dict(v, f"{new_key}_"))
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        if isinstance(item, dict):
                            flat_item = flatten_dict(item, f"{new_key}_{i}_")
                            items.update(flat_item)
                        else:
                            items[f"{new_key}_{i}"] = str(item)
                else:
                    items[new_key] = str(v)
            return items
        
        # Process each item in the list
        for item in json_list:
            if isinstance(item, dict):
                flattened = flatten_dict(item)
                rows.append(flattened)
                headers.update(flattened.keys())
        
        return rows, list(headers)

    def process_json_content(self, content: bytes) -> bytes:
        """Process JSON content and convert to Excel with improved handling of nested structures."""
        try:
            json_data = json.loads(content)
            
            # Convert single object to list
            if isinstance(json_data, dict):
                json_data = [json_data]
            elif not isinstance(json_data, list):
                raise ValueError("Invalid JSON format")

            # Process the JSON data
            rows, headers = self.flatten_json_list(json_data)
            
            # Create workbook
            wb = Workbook()
            sheet = wb.active
            
            # Write headers
            sheet.append(sorted(headers))
            
            # Write data rows
            for row in rows:
                row_data = [row.get(header, "") for header in sorted(headers)]
                sheet.append(row_data)

            # Save to bytes
            excel_buffer = io.BytesIO()
            wb.save(excel_buffer)
            excel_buffer.seek(0)
            return excel_buffer.getvalue()

        except Exception as e:
            raise Exception(f"Error processing JSON: {str(e)}")

    def analyze_trade_data(self, content: bytes, file_type: str) -> dict:
        """Analyze trade data for maturity dates before June 5, 2025."""
        try:
            target_date = datetime.strptime('2025-06-05', '%Y-%m-%d')
            
            if "json" in file_type.lower():
                data = json.loads(content)
                if not isinstance(data, list):
                    data = [data]
            elif "xml" in file_type.lower():
                root = ET.fromstring(content)
                data = [self.flatten_element(elem, {}) for elem in root]
            else:
                return {"error": "Unsupported file type for trade analysis"}

            trade_analysis = {
                "trades_before_maturity": [],
                "total_economic_value": 0
            }

            for trade in data:
                # Adapt these field names based on your actual trade data structure
                maturity_date = trade.get('maturityDate') or trade.get('maturity_date')
                strike_price = float(trade.get('strikePrice', 0) or trade.get('strike_price', 0))
                quantity = float(trade.get('quantity', 0))

                if maturity_date:
                    try:
                        trade_date = datetime.strptime(maturity_date, '%Y-%m-%d')
                        if trade_date < target_date:
                            economic_value = strike_price * quantity
                            trade_analysis["trades_before_maturity"].append({
                                "trade_id": trade.get('tradeId') or trade.get('trade_id', 'Unknown'),
                                "maturity_date": maturity_date,
                                "economic_value": economic_value
                            })
                            trade_analysis["total_economic_value"] += economic_value
                    except ValueError:
                        continue

            return trade_analysis

        except Exception as e:
            return {"error": f"Error analyzing trade data: {str(e)}"}

    def create_excel(self, content: bytes, file_type: str) -> bytes:
        """Create Excel file based on input content type"""
        try:
            if "xml" in file_type.lower():
                return self.process_xml_content(content)
            elif "json" in file_type.lower():
                return self.process_json_content(content)
            else:
                raise ValueError("Unsupported file type for Excel conversion")
                
        except Exception as e:
            error_wb = Workbook()
            error_sheet = error_wb.active
            error_sheet['A1'] = "Error Creating Excel File"
            error_sheet['A2'] = str(e)
            
            error_buffer = io.BytesIO()
            error_wb.save(error_buffer)
            error_buffer.seek(0)
            
            return error_buffer.getvalue()