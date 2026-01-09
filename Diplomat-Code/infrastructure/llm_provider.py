import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiProvider:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in .env file.")
        
        genai.configure(api_key=self.api_key)
        # Using the latest flash model alias for better availability
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def refine_message(self, original_content: str, target_tone: str, channel: str, context_notes: str) -> str:
        """
        Sends a prompt to Gemini to refine the message.
        """
        prompt = f"""
        Act as an expert communication diplomat and editor.
        
        Your Goal: Rewrite the following message to match the target tone: "{target_tone}".
        Output Format: The message is intended for a "{channel}" format. Adjust formatting, length, and style accordingly (e.g. Subject lines for emails, hashtags for social posts).
        
        Context/Constraints:
        {context_notes}
        
        Original Message:
        "{original_content}"
        
        Output Format:
        Return ONLY the refined message code. Do not include any introductory text like "Here is the refined message".
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip('`"') # Cleanup potential formatting
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                return "System is currently cooling down (Rate Limit). Please wait 30-60 seconds and try again."
            return f"Error generating suggestion: {str(e)}"

    def explain_changes(self, original: str, refined: str, tone: str) -> str:
        """
        Asks Gemini to explain why it made the changes.
        """
        prompt = f"""
        You just rewrote a message to be more "{tone}".
        
        Original: "{original}"
        New: "{refined}"
        
        Explain your changes in 1 single sentence. start with "I changed..."
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return "Could not generate explanation."
