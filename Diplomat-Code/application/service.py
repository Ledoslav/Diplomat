from domain.agent import DiplomatAgent
from domain.models import RefinedMessage, AppUser, Contact
from infrastructure.repository import Repository

class AgentService:
    def __init__(self):
        self.agent = DiplomatAgent()
        self.repository = Repository()
        
        # Temporary "Guest" user for guests
        self.guest_user = AppUser(username="guest", email="", password_hash="", self_context="")

    def register(self, username, email, password) -> bool:
        if self.repository.get_user(username):
            return False # Already exists
        
        new_user = AppUser(
            username=username,
            email=email,
            password_hash=self.repository.hash_password(password)
        )
        self.repository.save_user(new_user)
        return True

    def login(self, username, password) -> AppUser:
        user = self.repository.get_user(username)
        if user and user.password_hash == self.repository.hash_password(password):
            return user
        return None

    def update_context(self, user: AppUser, context: str):
        user.self_context = context
        self.repository.save_user(user)

    def change_username(self, user: AppUser, new_username: str) -> bool:
        if self.repository.update_username(user.username, new_username):
            user.username = new_username
            return True
        return False
    
    def delete_account(self, user: AppUser):
        self.repository.delete_user(user.username)

    def add_contact(self, user: AppUser, name: str, relation: str, desc: str):
        c = Contact(name=name, relationship=relation, description=desc)
        user.contacts.append(c)
        self.repository.save_user(user)

    def delete_contact(self, user: AppUser, contact_name: str):
        user.contacts = [c for c in user.contacts if c.name != contact_name]
        self.repository.save_user(user)

    def update_contact(self, user: AppUser, old_name: str, new_name: str, new_rel: str, new_desc: str):
        for c in user.contacts:
            if c.name == old_name:
                c.name = new_name
                c.relationship = new_rel
                c.description = new_desc
                break
        self.repository.save_user(user)

    def get_advice(self, user: AppUser, current_text: str, recipient: str, relation: str, tone: str, channel: str) -> RefinedMessage:
        # Use guest if no user provided
        active_user = user if user else self.guest_user
        
        # 1. Sense
        msg = self.agent.sense(current_text, recipient, relation, tone, channel)
        # 2. Think (Pass user for memory/context)
        refined = self.agent.think(msg, active_user)
        return refined

    def record_outcome(self, user: AppUser, refined: RefinedMessage, accepted: bool, final_text: str):
        active_user = user if user else self.guest_user
        # 4. Learn
        self.agent.learn(refined, accepted, final_text, active_user)

_service_instance = None
def get_service():
    global _service_instance
    if _service_instance is None:
        _service_instance = AgentService()
    return _service_instance
