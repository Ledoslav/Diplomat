import streamlit as st
from application.service import get_service
from domain.models import Tone, CommunicationChannel

# --- CONFIG & STYLING ---
# --- CONFIG & STYLING ---
st.set_page_config(page_title="Diplomat", page_icon="🕊️", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

def get_theme_css(theme):
    if theme == "Dark":
        return """
        <style>
            .stApp { background: rgb(14, 17, 23); color: #FAFAFA; }
            .stTextInput > div > div > input { background-color: #262730; color: white; }
            .stTextArea > div > div > textarea { background-color: #262730; color: white; }
            h1, h2, h3 { color: #D4AF37 !important; font-family: 'Helvetica Neue', sans-serif; }
            .highlight-reason { color: #4CAF50; font-style: italic; }
            
            /* Primary Button Styling (Gold) */
            div.stButton > button[kind="primary"] {
                background-color: #D4AF37 !important;
                color: rgb(14, 17, 23) !important;
                border-color: #D4AF37 !important;
            }
            div.stButton > button[kind="primary"]:hover {
                background-color: #C5A028 !important;
                color: rgb(14, 17, 23) !important;
            }
        </style>
        """
    else:
        return """
        <style>
            .stApp { background: #FFFFFF; color: #000000; }
            
            /* Inputs & Dropdowns */
            .stTextInput > div > div > input { background-color: #F0F2F6; color: black; }
            .stTextArea > div > div > textarea { background-color: #F0F2F6; color: black; }
            .stSelectbox div[data-baseweb="select"] > div {
                background-color: #F0F2F6 !important;
                color: black !important;
            }
            .stSelectbox div[data-baseweb="select"] span {
                color: black !important;
            }
            
            /* Headers */
            h1, h2, h3 { color: #1E3A8A !important; font-family: 'Helvetica Neue', sans-serif; } /* Navy Blue for contrast */
            
            /* Sidebar Specific Override */
            section[data-testid="stSidebar"] h1, 
            section[data-testid="stSidebar"] h2, 
            section[data-testid="stSidebar"] h3 { 
                color: #D4AF37 !important; 
            }
            
            .highlight-reason { color: #D32F2F; font-style: italic; }

            /* Primary Button Styling (Gold) */
            div.stButton > button[kind="primary"] {
                background-color: #D4AF37 !important;
                color: rgb(14, 17, 23) !important;
                border: 1px solid #D4AF37 !important;
            }
            div.stButton > button[kind="primary"]:hover {
                background-color: #C5A028 !important;
                color: rgb(14, 17, 23) !important;
            }
        </style>
        """

st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "agent_service" not in st.session_state:
    st.session_state.agent_service = get_service()

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "current_suggestion" not in st.session_state:
    st.session_state.current_suggestion = None  # Holds RefinedMessage


@st.dialog("Authentication")
def auth_dialog():
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        l_user = st.text_input("Username", key="l_user_modal")
        l_pass = st.text_input("Password", type="password", key="l_pass_modal")
        if st.button("Log In", key="btn_login_modal"):
            user = st.session_state.agent_service.login(l_user, l_pass)
            if user:
                st.session_state.current_user = user
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        s_user = st.text_input("Username", key="s_user_modal")
        s_email = st.text_input("Email", key="s_email_modal")
        s_pass = st.text_input("Password", type="password", key="s_pass_modal")
        s_pass2 = st.text_input("Repeat Password", type="password", key="s_pass2_modal")
        if st.button("Sign Up", key="btn_signup_modal"):
            if s_pass != s_pass2:
                st.error("Passwords do not match!")
            elif len(s_pass) < 1:
                st.error("Enter a password")
            else:
                # Calls register with email
                success = st.session_state.agent_service.register(s_user, s_email, s_pass)
                if success:
                    st.success("Account created! You can now log in.")
                else:
                    st.error("Username already exists.")

@st.dialog("Settings")
def settings_dialog():
    user = st.session_state.current_user
    st.subheader("Account")
    
    # Username Change
    new_username = st.text_input("Username", value=user.username)
    if st.button("Update Username"):
        if new_username != user.username:
            success = st.session_state.agent_service.change_username(user, new_username)
            if success:
                st.success("Username updated!")
                st.rerun()
            else:
                st.error("Username taken or invalid.")
    
    # Email View
    st.text_input("Email", value=user.email, disabled=True)
    
    st.markdown("---")
    st.subheader("Persona")
    new_context = st.text_area("About Me", value=user.self_context, height=100)
    if st.button("Update Persona"):
        st.session_state.agent_service.update_context(user, new_context)
        st.success("Saved!")
        
    st.markdown("---")
    st.subheader("App Preference")
    
    # Theme Toggle
    is_dark = st.session_state.theme == "Dark"
    toggle = st.toggle("Dark Mode", value=is_dark)
    
    # Logic to handle toggle change
    new_theme = "Dark" if toggle else "Light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()
        
    st.markdown("---")
    if st.button("🗑️ Delete Account", type="primary"): 
        st.session_state.confirm_delete_account = True
        st.rerun()

@st.dialog("Delete Account")
def delete_account_confirmation_dialog():
    st.warning("Are you sure you want to delete your account? This action cannot be undone.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Yes, Delete Account", type="primary"):
            st.session_state.agent_service.delete_account(st.session_state.current_user)
            st.session_state.current_user = None
            st.success("Account deleted.")
            # Clear trigger
            if "confirm_delete_account" in st.session_state:
                del st.session_state.confirm_delete_account
            st.rerun()
    with c2:
        if st.button("Cancel"):
            if "confirm_delete_account" in st.session_state:
                del st.session_state.confirm_delete_account
            st.rerun()

@st.dialog("Delete Contact")
def delete_contact_confirmation_dialog(contact_name):
    st.warning(f"Are you sure you want to delete {contact_name}?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Yes, Delete", type="primary"):
             user = st.session_state.current_user
             st.session_state.agent_service.delete_contact(user, contact_name)
             if st.session_state.get("selected_contact_name") == contact_name:
                st.session_state.selected_contact_name = "Custom"
             st.success("Deleted!")
             # Clear trigger
             if "confirm_delete_contact_name" in st.session_state:
                 del st.session_state.confirm_delete_contact_name
             st.rerun()
    with c2:
         if st.button("Cancel"):
             if "confirm_delete_contact_name" in st.session_state:
                 del st.session_state.confirm_delete_contact_name
             st.rerun()

@st.dialog("Add New Contact")
def contact_dialog():
    user = st.session_state.current_user
    c_name = st.text_input("Name")
    c_rel = st.selectbox("Relationship", ["Boss", "Colleague", "Friend", "Family", "Client", "Professor", "Student", "Romantic Interest", "Other"])
    c_desc = st.text_input("Notes (Optional)")
    
    if st.button("Save Contact"):
        if c_name:
            st.session_state.agent_service.add_contact(user, c_name, c_rel, c_desc)
            st.success("Saved!")
            st.rerun()
        else:
            st.error("Name is required")

@st.dialog("Edit Contact")
def edit_contact_dialog(contact_name):
    user = st.session_state.current_user
    # Find contact
    try:
        contact = next(c for c in user.contacts if c.name == contact_name)
    except StopIteration:
        st.error("Contact not found")
        # Ensure we don't crash if contact was deleted externally
        if st.button("Close"):
             st.rerun()
        return

    new_name = st.text_input("Name", value=contact.name)
    new_rel = st.selectbox("Relationship", ["Boss", "Colleague", "Friend", "Family", "Client", "Professor", "Student", "Romantic Interest", "Acquaintance", "Intern", "Subordinate", "Hiring Manager", "Service Provider", "Mentor", "Neighbour", "Stranger", "Other"], index=["Boss", "Colleague", "Friend", "Family", "Client", "Professor", "Student", "Romantic Interest", "Acquaintance", "Intern", "Subordinate", "Hiring Manager", "Service Provider", "Mentor", "Neighbour", "Stranger", "Other"].index(contact.relationship) if contact.relationship in ["Boss", "Colleague", "Friend", "Family", "Client", "Professor", "Student", "Romantic Interest", "Acquaintance", "Intern", "Subordinate", "Hiring Manager", "Service Provider", "Mentor", "Neighbour", "Stranger", "Other"] else 8)
    new_desc = st.text_input("Notes (Optional)", value=contact.description)
    
    col_save, col_del = st.columns([1, 1])
    with col_save:
        if st.button("Save Changes", type="primary"):
            st.session_state.agent_service.update_contact(user, contact.name, new_name, new_rel, new_desc)
            st.success("Updated!")
            st.rerun()
    
    with col_del:
        if st.button("🗑️ Delete Contact", type="primary"): 
            st.session_state.confirm_delete_contact_name = contact.name
            st.rerun()

@st.dialog("Message History", width="large")
def history_dialog():
    user = st.session_state.current_user
    history = sorted(user.memory.history, key=lambda x: x.timestamp, reverse=True)
    
    if not history:
        st.info("No history found.")
        return

    # Filter
    all_recipients = set(h.message.recipient_name for h in history)
    recipients = ["All"] + sorted(list(all_recipients))
    
    selected_recipient = st.selectbox("Filter by Recipient", recipients)
    
    if selected_recipient != "All":
        history = [h for h in history if h.message.recipient_name == selected_recipient]
    
    st.markdown("---")
    
    for h in history:
        with st.container(border=True):
            cols = st.columns([3, 1])
            cols[0].markdown(f"**To:** {h.message.recipient_name}")
            cols[1].caption(h.timestamp.strftime("%Y-%m-%d %H:%M"))
            
            st.caption("Original Draft")
            st.text(h.message.content)
            
            st.caption("Agent Response")
            st.markdown(f"```text\n{h.final_content}\n```")
            
            if h.accepted:
                st.caption("✅ Accepted")
            else:
                st.caption("❌ Rejected")

# --- SIDEBAR (Context & Auth) ---
with st.sidebar:
    st.title("🕊️ Diplomat")
    
    # --- AUTH SECTION ---
    if st.session_state.current_user is None:
        st.subheader("Guest Mode")
        st.info("Log in to save contacts and learn your style.")
        
        if st.button("👤Sign In / Log In", type="primary"):
            auth_dialog()
            
        st.markdown("---")
        # Guest Theme Toggle
        is_dark = st.session_state.theme == "Dark"
        if st.toggle("Dark Mode", value=is_dark, key="guest_theme_toggle"):
            st.session_state.theme = "Dark"
        else:
            st.session_state.theme = "Light"
        # We need to rerun to apply css if changed, but toggle usually triggers rerun.
        # Adding an explicit check to force update if state diverges:
        if (st.session_state.theme == "Dark") != is_dark:
             st.rerun()

    else:
        # --- LOGGED IN USER VIEW ---
        user = st.session_state.current_user
        st.subheader(f"👤 User: {user.username}")
        
        if st.button("➜] Logout"):
            st.session_state.current_user = None
            st.rerun()

        if st.button("📜 History"):
            history_dialog()

        if st.button("⚙️ Settings"):
            settings_dialog()
        
        st.markdown("---")
        st.markdown("### 📒 Saved Contacts")
        
        if st.button("➕ Add New Contact"):
            contact_dialog()
            
        
        # Ensure state exists
        if "selected_contact_name" not in st.session_state:
            st.session_state.selected_contact_name = "Custom"
            
        # Custom Button
        if st.button("Custom", 
                     type="primary" if st.session_state.selected_contact_name == "Custom" else "secondary", 
                     use_container_width=True):
            st.session_state.selected_contact_name = "Custom"
            st.rerun()
            
        # List Contacts
        for c in user.contacts:
            c1, c2 = st.columns([0.8, 0.2])
            with c1:
                if st.button(c.name, 
                             key=f"btn_sel_{c.name}", 
                             type="primary" if st.session_state.selected_contact_name == c.name else "secondary",
                             use_container_width=True):
                    st.session_state.selected_contact_name = c.name
                    st.rerun()
            with c2:
                if st.button("⚙️", key=f"btn_edit_{c.name}", type="tertiary"):
                    edit_contact_dialog(c.name)

# --- MAIN AREA ---

# Layout: Left (Draft & Action) | Right (Configuration)
c_main, c_side = st.columns([3, 1])

# --- RIGHT SIDE (Configuration) ---
with c_side:
    st.markdown("### Context")
    
    # Recipient Config
    recipient_name = ""
    relationship = ""
    
    # Determine selection source
    if st.session_state.current_user:
        selected_contact_name = st.session_state.get("selected_contact_name", "Custom")
    else:
        selected_contact_name = "Custom"
        st.session_state.selected_contact_name = "Custom"

    if selected_contact_name != "Custom" and st.session_state.current_user:
        try:
            contact = next(c for c in st.session_state.current_user.contacts if c.name == selected_contact_name)
            recipient_name = st.text_input("Recipient Name", value=contact.name, disabled=True)
            relationship = st.text_input("Relationship", value=contact.relationship, disabled=True)
        except StopIteration:
            st.session_state.selected_contact_name = "Custom"
            st.rerun()
    else:
        recipient_name = st.text_input("Recipient Name", placeholder="e.g., Mr. Smith")
        relationship = st.selectbox(
            "Relationship", 
            ["Boss", "Colleague", "Friend", "Family", "Client", "Professor", "Student", "Romantic Interest", "Acquaintance", "Intern", "Subordinate", "Hiring Manager", "Service Provider", "Mentor", "Neighbour", "Stranger", "Other"]
        )

    tone = st.selectbox("Target Tone", [t.value for t in Tone])
    channel = st.selectbox("Format", [c.value for c in CommunicationChannel])
    
    msg_context = st.text_area("Situation Context", height=130)
    st.info("Optional: Add specific context (e.g., 'They are angry').")

# --- LEFT SIDE (Draft & Action) ---
with c_main:
    st.markdown("### 📝Drafting")
    user_draft = st.text_area("Draft your message here...", height=500, placeholder="e.g., Hey u, send me the files ASAP.")
    analyze_btn = st.button("✨ Analyze & Refine", type="primary", use_container_width=True)

# --- LOGIC FLOW ---

if analyze_btn and user_draft:
    # AppendContext
    full_text_to_analyze = user_draft
    if msg_context:
        full_text_to_analyze = f"[Context: {msg_context}] \nMessage: {user_draft}"

    with st.spinner("Thinking..."):
        suggestion = st.session_state.agent_service.get_advice(
            st.session_state.current_user, 
            full_text_to_analyze, 
            recipient_name, 
            relationship, 
            tone,
            channel
        )
        st.session_state.current_suggestion = suggestion
        st.session_state.suggestion_status = "pending"

# Display Result
if st.session_state.current_suggestion:
    refined = st.session_state.current_suggestion
    
    st.markdown("---")
    st.subheader("💡 Suggestion")
    st.markdown(f"```text\n{refined.suggested_content}\n```")
    st.markdown(f"**Reasoning**: <span class='highlight-reason'>{refined.reasoning}</span>", unsafe_allow_html=True)
    
    st.markdown("### Decision")
    
    # Check status (default to pending if missing)
    status = st.session_state.get("suggestion_status", "pending")
    
    if status == "pending":
        b1, b2, b3 = st.columns([1, 1, 4])
        
        if b1.button("✅ Accept"):
            st.session_state.agent_service.record_outcome(
                st.session_state.current_user, refined, True, refined.suggested_content
            )
            st.toast("Learned: You liked this style!")
            st.session_state.suggestion_status = "accepted"
            st.rerun()
        
        if b2.button("❌ Reject"):
            st.session_state.agent_service.record_outcome(
                st.session_state.current_user, refined, False, refined.original_message.content
            )
            st.toast("Learned: You disliked this style.")
            st.session_state.suggestion_status = "rejected"
            st.rerun()
            
    else:
        st.info("Thank you for your feedback!")

    # Show Regenerate if rejected
    if status == "rejected":
        if st.button("🔄 Regenerate Response"):
             # Re-run logic with same params
             full_text_to_analyze = user_draft
             if msg_context:
                full_text_to_analyze = f"[Context: {msg_context}] \nMessage: {user_draft}"
             
             with st.spinner("Regenerating..."):
                suggestion = st.session_state.agent_service.get_advice(
                    st.session_state.current_user, 
                    full_text_to_analyze, 
                    recipient_name, 
                    relationship, 
                    tone,
                    channel
                )
                st.session_state.current_suggestion = suggestion
                st.session_state.suggestion_status = "pending"
                st.rerun()

# --- DIALOG TRIGGERS ---
if "confirm_delete_account" in st.session_state:
    delete_account_confirmation_dialog()

if "confirm_delete_contact_name" in st.session_state:
    delete_contact_confirmation_dialog(st.session_state.confirm_delete_contact_name)
