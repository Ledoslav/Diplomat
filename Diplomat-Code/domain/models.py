from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class Tone(Enum):
    FORMAL = "Formal"
    CASUAL = "Casual"
    FRIENDLY = "Friendly"
    ASSERTIVE = "Assertive"
    PROFESSIONAL = "Professional"
    FLIRTY = "Flirty"
    MISCHIEVOUS = "Mischievous"
    HUMOROUS = "Humorous"
    EMPATHETIC = "Empathetic"
    APOLOGETIC = "Apologetic"
    DIPLOMATIC = "Diplomatic"
    URGENT = "Urgent"
    PERSUASIVE = "Persuasive"
    WITTY = "Witty"
    CONCISE = "Concise"
    ENCOURAGING = "Encouraging"

class CommunicationChannel(Enum):
    CHAT = "Chat Message"
    SMS = "SMS / Text Message"
    EMAIL = "Email"
    PROFESSIONAL_CHAT = "Professional Chat (Slack/Teams)"
    LINKEDIN = "LinkedIn Message"
    DATING_APP = "Dating App Message"
    SOCIAL_POST = "Social Media Post"
    CAPTION = "Caption"
    COMMENT = "Comment / Reply"
    FORMAL_LETTER = "Formal Letter"
    REVIEW = "Review"
    FEEDBACK = "Feedback"

@dataclass
class Message:
    content: str
    recipient_name: str
    recipient_relationship: str  # e.g., "Boss", "Mother", "Client"
    intended_tone: Tone
    channel: CommunicationChannel = CommunicationChannel.CHAT
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RefinedMessage:
    original_message: Message
    suggested_content: str
    reasoning: str
    changes_made: List[str]

@dataclass
class Interaction:
    message: Message
    refined_message: RefinedMessage
    accepted: bool
    final_content: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Contact:
    name: str
    relationship: str # e.g. "Boss"
    description: str = "" # Optional specific context

@dataclass
class AgentMemory:
    """
    The 'Memory' of the agent for a specific user.
    Tracks preferences per relationship type.
    """
    relationship_preferences: Dict[str, Dict[str, float]] = field(default_factory=dict)
    history: List[Interaction] = field(default_factory=list)

    def add_history(self, interaction: Interaction):
        self.history.append(interaction)

@dataclass
class AppUser:
    username: str
    email: str
    password_hash: str # Simple hashing for this class
    self_context: str = "" # e.g. "Software Engineer at Google"
    contacts: List[Contact] = field(default_factory=list)
    memory: AgentMemory = field(default_factory=AgentMemory)
