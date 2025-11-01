import streamlit as st
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import re
from dotenv import load_dotenv

# ============ LOAD ENVIRONMENT VARIABLES ============
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")
smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
smtp_port = int(os.getenv("SMTP_PORT", 587))

# ============ PAGE CONFIG ============
st.set_page_config(page_title="AI Email Assistant", page_icon="✉️", layout="centered")

# ============ SESSION STATE ============
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_email" not in st.session_state:
    st.session_state.generated_email = ""
if "email_subject" not in st.session_state:
    st.session_state.email_subject = ""
if "recipient_email" not in st.session_state:
    st.session_state.recipient_email = ""
if "attachments" not in st.session_state:
    st.session_state.attachments = []
if "awaiting_confirmation" not in st.session_state:
    st.session_state.awaiting_confirmation = False


# ============ FUNCTIONS ============
def generate_email(prompt, api_key, chat_history=None):
    """Generate or refine email using Gemini API."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        context = ""
        if chat_history:
            for msg in chat_history:
                role = "User" if msg["role"] == "user" else "AI"
                context += f"{role}: {msg['content']}\n"

        enhanced_prompt = f"""
        You are an AI email assistant that helps draft and refine professional emails.
        Always use the following format:
        Subject: <subject line>
        <email body>

        Fill in missing details by asking the user politely.
        If the user requests to send or share an email, identify the recipient email and prepare for confirmation.
        Use simple, polite English and business tone.

        Conversation so far:
        {context}
        User: {prompt}
        """

        response = model.generate_content(enhanced_prompt)
        email_content = response.text.strip()

        if "Subject:" in email_content:
            parts = email_content.split("Subject:", 1)
            subject_and_body = parts[1].strip()
            if "\n" in subject_and_body:
                subject = subject_and_body.split("\n", 1)[0].strip()
                body = subject_and_body.split("\n", 1)[1].strip()
            else:
                subject = "Email from AI Assistant"
                body = subject_and_body
        else:
            subject = "Email from AI Assistant"
            body = email_content

        return subject, body

    except Exception as e:
        return None, f"Error generating email: {str(e)}"


def send_email(recipient_email, subject, body, attachments=None):
    """Send email with optional attachments."""
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        if attachments:
            for file in attachments:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.getvalue())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={file.name}")
                msg.attach(part)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        return True, f"✅ Email successfully sent to {recipient_email}"

    except Exception as e:
        return False, f"❌ Failed to send email: {str(e)}"


def detect_send_intent(prompt: str):
    """Detect if user intends to send/share email."""
    keywords = ["send", "share", "mail", "forward", "deliver", "dispatch"]
    return any(kw in prompt.lower() for kw in keywords)


# ============ CHAT DISPLAY ============
st.title("🤖 AI Email Assistant")
st.markdown("Chat naturally — draft, refine, and send emails. Add attachments and confirm before sending.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ============ ATTACHMENT UI ============
# if st.session_state.generated_email and not st.session_state.awaiting_confirmation:
#     add_attachment = st.toggle("📎 Add attachment?")
#     if add_attachment:
#         uploaded_files = st.file_uploader("Upload your attachments", accept_multiple_files=True)
#         if uploaded_files:
#             st.session_state.attachments = uploaded_files
#             st.success(f"{len(uploaded_files)} attachment(s) ready to include.")

# ============ CHAT INPUT ============
# ============ CHAT INPUT ============
if api_key:
    user_prompt = st.chat_input("Type something (e.g., 'Write an email to HR about leave', 'Send this to john@example.com')")

    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Case 1: User is confirming send
                if st.session_state.awaiting_confirmation:
                    if user_prompt.lower().strip() in ["yes", "y"]:
                        success, message = send_email(
                            st.session_state.recipient_email,
                            st.session_state.email_subject,
                            st.session_state.generated_email,
                            st.session_state.attachments,
                        )
                        st.session_state.awaiting_confirmation = False
                        st.session_state.attachments = []
                        st.session_state.messages.append({"role": "assistant", "content": message})
                        st.markdown(message)

                    elif user_prompt.lower().strip() in ["no", "n", "cancel"]:
                        st.session_state.awaiting_confirmation = False
                        msg = "❎ Email sending cancelled."
                        st.session_state.messages.append({"role": "assistant", "content": msg})
                        st.markdown(msg)
                    else:
                        st.warning("Please type 'yes' to send or 'no' to cancel.")

                # Case 2: Asking about attachments
                elif "attachment" in user_prompt.lower() or "attach" in user_prompt.lower():
                    uploaded_files = st.file_uploader("Upload your attachments here", accept_multiple_files=True)
                    if uploaded_files:
                        st.session_state.attachments = uploaded_files
                        msg = f"📎 {len(uploaded_files)} attachment(s) added. Ready to send or continue editing?"
                        st.session_state.messages.append({"role": "assistant", "content": msg})
                        st.markdown(msg)
                    else:
                        st.info("No attachments selected yet.")

                # Case 3: Detect intent to send
                elif detect_send_intent(user_prompt):
                    match = re.search(r"[\w\.-]+@[\w\.-]+", user_prompt)
                    if match:
                        st.session_state.recipient_email = match.group(0)
                    elif not st.session_state.recipient_email:
                        msg = "Please provide the recipient’s email address."
                        st.session_state.messages.append({"role": "assistant", "content": msg})
                        st.markdown(msg)
                        st.stop()

                    if not st.session_state.generated_email:
                        msg = "⚠️ Please generate an email first. What should I write?"
                        st.session_state.messages.append({"role": "assistant", "content": msg})
                        st.markdown(msg)
                    else:
                        st.session_state.awaiting_confirmation = True
                        confirm_msg = (
                            f"### ✉️ Confirm Before Sending\n"
                            f"**To:** {st.session_state.recipient_email}\n\n"
                            f"**Subject:** {st.session_state.email_subject}\n\n"
                            f"{st.session_state.generated_email}\n\n"
                            f"Would you like me to send this? (yes/no)"
                        )
                        st.session_state.messages.append({"role": "assistant", "content": confirm_msg})
                        st.markdown(confirm_msg)

                # Case 4: Normal email generation/refinement
                else:
                    subject, body = generate_email(user_prompt, api_key, st.session_state.messages)
                    if subject:
                        st.session_state.email_subject = subject
                        st.session_state.generated_email = body
                        ai_reply = f"**Subject:** {subject}\n\n{body}\n\n"
                        st.markdown(ai_reply)
                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    else:
                        st.markdown(body)
                        st.session_state.messages.append({"role": "assistant", "content": body})
else:
    st.error("⚙️ Please set your GEMINI_API_KEY in the .env file to start chatting.")

