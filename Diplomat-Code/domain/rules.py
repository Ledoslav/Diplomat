from domain.models import Tone
from infrastructure.llm_provider import GeminiProvider

class RuleEngine:
    """
    The 'Think' component - upgraded to use LLM.
    """
    def __init__(self):
        self.llm = GeminiProvider()

    def refine_message(self, content: str, target_tone: Tone, channel: str, recipient_history: dict, personal_context: str = "") -> (str, str, list):
        """
        Uses Gemini to refine the message.
        """
        # 1. Construct Learning Context
        # Check history scores to advise the LLM
        context_notes = ""
        
        if personal_context:
            context_notes += f"USER CONTEXT (The Sender): {personal_context}\n"

        tone_score = recipient_history.get(target_tone.value, 0)
        
        if tone_score < 0:
            context_notes += f"WARNING: The user has previously REJECTED suggestions for '{target_tone.value}' tone. Please be very subtle and close to the original text. Do not overdo it.\n"
        elif tone_score > 3:
            context_notes += f"NOTE: The user LOVES this '{target_tone.value}' tone. You can be very expressive and fully embrace this style.\n"
        
        # 2. Call LLM for Refinement (Think)
        refined_content = self.llm.refine_message(content, target_tone.value, channel, context_notes)
        
        # 3. Call LLM for Explanation
        explanation = self.llm.explain_changes(content, refined_content, target_tone.value)
        
        # 4. Changes List (heuristic diff for UI)
        changes = ["Used Generative AI for total rewrite"]
        
        return refined_content, explanation, changes
