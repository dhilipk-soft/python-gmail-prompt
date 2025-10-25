"""
Simplified Email Generator with Gemini AI
A minimal version for quick testing
"""
import os
import streamlit as st
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.title("✉️ Email Generator with Gemini AI")

# Sidebar for API key
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Gemini API Key:", type="password", value=os.getenv("GEMINI_API_KEY"))
    st.markdown("[Get your free API key](https://makersuite.google.com/app/apikey)")
# Main interface
col1, col2 = st.columns(2)

with col1:
    st.header("Generate Email")
    prompt = st.text_area(
        "What email do you need?",
        placeholder="Example: Write a sick leave email for tomorrow",
        height=100
    )
    
    if st.button("Generate Email", type="primary"):
        if not api_key:
            st.error("Please enter your Gemini API key!")
        elif not prompt:
            st.error("Please enter what kind of email you need!")
        else:
            with st.spinner("Generating email..."):
                try:
                    # Configure Gemini
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    # Generate email
                    enhanced_prompt = f"""Write a professional email for: {prompt}
                    
                    Format:
                    Subject: [subject line]
                    
                    [Email body with proper greeting, content, and closing]"""
                    
                    response = model.generate_content(enhanced_prompt)
                    st.session_state['email'] = response.text
                    st.success("Email generated!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Display generated email
if 'email' in st.session_state:
    st.header("Generated Email")
    st.text_area("Your Email:", st.session_state['email'], height=300)
    
    with col2:
        st.header("Send Email")
        
        # Email settings
        sender_email = st.text_input("Your Email:",value=os.getenv("SENDER_EMAIL", ""))
        sender_password = st.text_input("App Password:", type="password", value=os.getenv("SENDER_PASSWORD", ""))
        recipient = st.text_input("Recipient Email:")
        
        smtp_provider = st.selectbox(
            "Email Provider:",
            ["Gmail", "Outlook", "Yahoo", "Custom"]
        )
        
        if smtp_provider == "Gmail":
            smtp_server, smtp_port = "smtp.gmail.com", 587
        elif smtp_provider == "Outlook":
            smtp_server, smtp_port = "smtp-mail.outlook.com", 587
        elif smtp_provider == "Yahoo":
            smtp_server, smtp_port = "smtp.mail.yahoo.com", 587
        else:
            smtp_server = st.text_input("SMTP Server:")
            smtp_port = st.number_input("SMTP Port:", value=587)
        
        if st.button("Send Email", type="primary"):
            if not all([sender_email, sender_password, recipient]):
                st.error("Please fill all email fields!")
            else:
                try:
                    # Parse subject and body
                    email_text = st.session_state['email']
                    if "Subject:" in email_text:
                        parts = email_text.split("Subject:", 1)[1].split("\n", 1)
                        subject = parts[0].strip()
                        body = parts[1].strip() if len(parts) > 1 else ""
                    else:
                        subject = "Email"
                        body = email_text
                    
                    # Send email
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = recipient
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'plain'))
                    
                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                        server.starttls()
                        server.login(sender_email, sender_password)
                        server.send_message(msg)
                    
                    st.success("Email sent successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error sending: {str(e)}")
                    if "Gmail" in smtp_provider:
                        st.info("💡 For Gmail, use an App Password, not your regular password!")

# Instructions at the bottom
st.divider()
st.markdown("""
### Quick Guide:
1. Get your free Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. For Gmail: Use an [App Password](https://myaccount.google.com/apppasswords) instead of your regular password
3. Generate your email with any prompt
4. Review, edit if needed, and send!

**Security Note:** Never share your API keys or passwords. Use app-specific passwords when available.
""")
