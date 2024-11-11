# ollama_service.py
import requests
from typing import Optional, Dict, Any

class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama3.2"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        self.model_name = model_name

    def generate_response(self, content: str, prompt: str) -> Optional[str]:
        """Generate response using Ollama API"""
        data = {
            "model": self.model_name,
            "prompt": self._format_prompt(prompt, content),
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            elif response.status_code == 404:
                error_msg = response.json().get("error", "")
                if "model" in error_msg.lower():
                    available_models = self._get_available_models()
                    return f"Error: Model '{self.model_name}' not found. Available models: {', '.join(available_models)}"
                return f"Error: {error_msg}"
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def _get_available_models(self) -> list:
        """Get list of available models from Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return [model["name"] for model in response.json()["models"]]
            return []
        except:
            return []

    def _format_prompt(self, prompt: str, content: str) -> str:
        """Format prompt with content for better responses"""
        return f"""
Instructions: {prompt}

Content:
{content}

Please provide a detailed and well-structured response based on the above content.
"""

    def generate_summary(self, content: str, file_type: str) -> str:
        prompt = f"""Please provide a comprehensive summary of the following {file_type} content. 
Include key points, main topics, and important details. Structure the summary in a clear and readable format."""
        return self.generate_response(content, prompt)

    def query_document(self, content: str, query: str) -> str:
        prompt = f"""Question: {query}

Please provide a detailed answer based on the document content only. 
If the answer cannot be found in the document, please indicate that."""
        return self.generate_response(content, query)