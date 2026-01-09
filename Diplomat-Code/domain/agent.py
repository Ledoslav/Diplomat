from domain.models import Message, RefinedMessage, Interaction, AppUser, Tone, CommunicationChannel
from domain.rules import RuleEngine
from infrastructure.repository import Repository
import datetime

class DiplomatAgent:
    def __init__(self):
        self.repository = Repository()
        self.brain = RuleEngine()

    # --- 1. SENSE ---
    def sense(self, content: str, recipient: str, relation: str, tone_str: str, channel_str: str) -> Message:
        """
        Gather input and context.
        """
        try:
            tone = Tone(tone_str)
        except ValueError:
            tone = Tone.PROFESSIONAL

        try:
            channel = CommunicationChannel(channel_str)
        except ValueError:
            channel = CommunicationChannel.CHAT

        return Message(
            content=content,
            recipient_name=recipient,
            recipient_relationship=relation,
            intended_tone=tone,
            channel=channel
        )

    # --- 2. THINK ---
    def think(self, message: Message, user: AppUser) -> RefinedMessage:
        """
        Process with User Context.
        """
        # Retrieve context from user's memory
        recipient_history_stats = user.memory.relationship_preferences.get(message.recipient_relationship, {})
        
        # Inject Self Context (The "I am a Doctor" part)
        # We pass this into the RuleEngine/LLM
        personal_context = user.self_context
        
        # Delegate
        new_content, explanation, changes = self.brain.refine_message(
            message.content, 
            message.intended_tone,
            message.channel.value,
            recipient_history_stats,
            personal_context
        )
        
        return RefinedMessage(
            original_message=message,
            suggested_content=new_content,
            reasoning=explanation,
            changes_made=changes
        )

    # --- 3. ACT ---
    def act(self, refined: RefinedMessage) -> dict:
        return {
            "original": refined.original_message.content,
            "suggestion": refined.suggested_content,
            "reasoning": refined.reasoning,
            "changes": refined.changes_made
        }

    # --- 4. LEARN ---
    def learn(self, refined: RefinedMessage, user_accepted: bool, final_content: str, user: AppUser):
        """
        Update User's specific memory.
        """
        interaction = Interaction(
            message=refined.original_message,
            refined_message=refined,
            accepted=user_accepted,
            final_content=final_content,
            timestamp=datetime.datetime.now()
        )
        
        # update memory
        user.memory.add_history(interaction)
        
        rel = refined.original_message.recipient_relationship
        tone_key = refined.original_message.intended_tone.value
        
        if rel not in user.memory.relationship_preferences:
            user.memory.relationship_preferences[rel] = {}
        
        current_score = user.memory.relationship_preferences[rel].get(tone_key, 0)
        
        if user_accepted:
            # Slower increment, maybe?
            user.memory.relationship_preferences[rel][tone_key] = current_score + 1
        else:
            user.memory.relationship_preferences[rel][tone_key] = current_score - 1
            
        # Persist User
        self.repository.save_user(user)
