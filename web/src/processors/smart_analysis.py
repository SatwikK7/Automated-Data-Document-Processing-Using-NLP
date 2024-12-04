from typing import Dict

class SmartAnalysisService:
    def __init__(self, ollama_service):
        self.ollama_service = ollama_service

    def analyze_trades(self, content: bytes, file_type: str) -> Dict:
        """Let Ollama analyze the content and determine if it's trade-related and provide analysis."""
        try:
            content_str = content.decode("utf-8")  # Ensure the content is a string (assuming UTF-8 encoding)
            
            # Send the content to Ollama to analyze for trade-related content
            prompt = """
            Analyze the following document for trade-related content. Keep it crisp
            If it's trade-related, provide smart trade analysis including basic metrics, risk analysis, market impact, and AI insights, Dont give information about each trade. Just insights and smart analysis, 
            also if any trade's maturity date is before June 5 2025, give its trade economics (i.e its strike pice*its quantity)
            If it's not trade-related, return an error message saying 'This feature is only for trade-related files.'
            """
            analysis_response = self.ollama_service.generate_response(content_str, prompt)
            
            if "error" in analysis_response.lower():
                return {"error": analysis_response}  # Return error if not trade-related
            
            # Return the analysis from Ollama if trade-related
            return {"analysis": analysis_response}
            
        except Exception as e:
            return {"error": f"Error in smart analysis: {str(e)}"}
