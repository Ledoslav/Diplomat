import json
import os
import hashlib
from typing import Optional, Dict
from domain.models import AppUser, AgentMemory, Interaction, Message, RefinedMessage, Tone, Contact
from datetime import datetime

class Repository:
    def __init__(self, storage_path: str = "d:/Diplomat/users_v2.json"):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w") as f:
                json.dump({"users": {}}, f)

    def _load_data(self) -> dict:
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except Exception:
            return {"users": {}}

    def _save_data(self, data: dict):
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=4, default=str)

    # --- User Management ---

    def get_user(self, username: str) -> Optional[AppUser]:
        data = self._load_data()
        users_data = data.get("users", {})
        
        if username not in users_data:
            return None
            
        u_data = users_data[username]
        
        # Reconstruct Objects
        user = AppUser(
            username=username,
            email=u_data.get("email", ""),
            password_hash=u_data.get("password_hash", ""),
            self_context=u_data.get("self_context", "")
        )
        
        # Contacts
        for c in u_data.get("contacts", []):
            user.contacts.append(Contact(name=c["name"], relationship=c["relationship"], description=c.get("description", "")))
            
        # Memory
        mem_data = u_data.get("memory", {})
        user.memory.relationship_preferences = mem_data.get("relationship_preferences", {})
        
        # Load History
        for h_data in mem_data.get("history", []):
            try:
                # Reconstruct Message
                orig_data = h_data["original_message"]
                msg = Message(
                    content=orig_data["content"],
                    recipient_name=orig_data["recipient"],
                    recipient_relationship="", # Not stored in v2 history schema explicitly, can infer or leave empty
                    intended_tone=Tone(orig_data["tone"])
                )
                
                # Reconstruct RefinedMessage (Partial)
                ref_msg = RefinedMessage(
                    original_message=msg,
                    suggested_content=h_data["refined_suggestion"],
                    reasoning="", # Not stored
                    changes_made=[] # Not stored
                )
                
                # Reconstruct Interaction
                interaction = Interaction(
                    message=msg,
                    refined_message=ref_msg,
                    accepted=h_data["accepted"],
                    final_content=h_data["final_content"],
                    timestamp=datetime.fromisoformat(h_data["timestamp"])
                )
                user.memory.history.append(interaction)
            except Exception as e:
                # robust against malformed history entries
                pass
        
        return user

    def save_user(self, user: AppUser):
        data = self._load_data()
        
        # Serialize User
        user_dict = {
            "email": user.email,
            "password_hash": user.password_hash,
            "self_context": user.self_context,
            "contacts": [
                {"name": c.name, "relationship": c.relationship, "description": c.description}
                for c in user.contacts
            ],
            "memory": {
                "relationship_preferences": user.memory.relationship_preferences,
                "history": [self._interaction_to_dict(i) for i in user.memory.history]
                # Note: This appends history every time. 
                # Optimization: In a real app we wouldn't rewrite the whole history array every save.
            }
        }
        
        data["users"][user.username] = user_dict
        self._save_data(data)

    def _interaction_to_dict(self, interaction: Interaction) -> dict:
        return {
            "timestamp": interaction.timestamp.isoformat(),
            "accepted": interaction.accepted,
            "final_content": interaction.final_content,
            "original_message": {
                "content": interaction.message.content,
                "recipient": interaction.message.recipient_name,
                "tone": interaction.message.intended_tone.value
            },
            "refined_suggestion": interaction.refined_message.suggested_content
        }

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def update_username(self, old_username: str, new_username: str) -> bool:
        data = self._load_data()
        users = data.get("users", {})
        
        if new_username in users:
            return False # Taken
        
        if old_username not in users:
            return False # Old doesn't exist?
            
        # Swap
        user_data = users[old_username]
        users[new_username] = user_data
        del users[old_username]
        
        self._save_data(data)
        return True

    def delete_user(self, username: str):
        data = self._load_data()
        if username in data.get("users", {}):
            del data["users"][username]
            self._save_data(data)
