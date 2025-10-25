import streamlit as st
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Email Generator & Sender",
    page_icon="✉️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextArea>div>div>textarea {
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'generated_email' not in st.session_state:
    st.session_state.generated_email = ""
if 'email_subject' not in st.session_state:
    st.session_state.email_subject = ""

def generate_email(prompt, api_key):
    """Generate email using Google Gemini AI"""
    try:
        # Configure Gemini AI
        genai.configure(api_key=api_key)
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Enhanced prompt for better email generation
        enhanced_prompt = f"""You are a professional email writer. Generate a well-formatted, professional email based on this request: {prompt}
        
        The email should:
        1. Have an appropriate subject line (start with "Subject: ")
        2. Include proper greeting
        3. Have clear, concise body content
        4. Include appropriate closing
        5. Be professional and polite in tone
        
        Format the response with the subject line first (after "Subject: "), followed by the email body.
        
        User's request: {prompt}"""
        
        # Generate content
        response = model.generate_content(enhanced_prompt)
        email_content = response.text
        
        # Extract subject and body
        if "Subject:" in email_content:
            parts = email_content.split("Subject:", 1)
            if len(parts) > 1:
                subject_and_body = parts[1].strip()
                if "\n" in subject_and_body:
                    subject = subject_and_body.split("\n", 1)[0].strip()
                    body = subject_and_body.split("\n", 1)[1].strip()
                else:
                    subject = "Email from AI Generator"
                    body = subject_and_body
            else:
                subject = "Email from AI Generator"
                body = email_content
        else:
            subject = "Email from AI Generator"
            body = email_content
            
        return subject, body
        
    except Exception as e:
        return None, f"Error generating email: {str(e)}"

def send_email(sender_email, sender_password, recipient_email, subject, body, smtp_server, smtp_port):
    """Send email using SMTP"""
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        
        # Add body to email
        message.attach(MIMEText(body, "plain"))
        
        # Create SMTP session
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Enable TLS encryption
            server.login(sender_email, sender_password)
            text = message.as_string()
            server.sendmail(sender_email, recipient_email, text)
            
        return True, "Email sent successfully!"
        
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

# Main UI
st.title("🤖 AI Email Generator & Sender")
st.markdown("Generate professional emails using AI and send them automatically!")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Gemini AI Configuration
    st.subheader("Google Gemini AI Settings")
    api_key = st.text_input("Gemini API Key", type="password", 
                            value=os.getenv("GEMINI_API_KEY", ""),
                            help="Enter your Google Gemini API key")
    
    st.divider()
    
    # Email Configuration
    st.subheader("Email Settings")
    
    # SMTP Provider selection
    smtp_provider = st.selectbox(
        "Email Provider",
        ["Gmail", "Outlook/Hotmail", "Yahoo", "Custom SMTP"]
    )
    
    # Set SMTP settings based on provider
    if smtp_provider == "Gmail":
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        st.info("📌 For Gmail: Use an App Password instead of your regular password. Enable 2FA and generate an app password.")
    elif smtp_provider == "Outlook/Hotmail":
        smtp_server = "smtp-mail.outlook.com"
        smtp_port = 587
    elif smtp_provider == "Yahoo":
        smtp_server = "smtp.mail.yahoo.com"
        smtp_port = 587
        st.info("📌 For Yahoo: Use an App Password instead of your regular password.")
    else:
        smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
        smtp_port = st.number_input("SMTP Port", value=587, min_value=1)
    
    sender_email = st.text_input("Your Email Address", 
                                 value=os.getenv("SENDER_EMAIL", ""))
    sender_password = st.text_input("Email Password/App Password", 
                                   type="password",
                                   value=os.getenv("SENDER_PASSWORD", ""),
                                   help="Use App Password for Gmail/Yahoo")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Generate Email")
    
    # Email prompt input
    prompt = st.text_area(
        "Enter your email request:",
        placeholder="Example: Write a professional leave request email for 2 days due to personal reasons",
        height=100
    )
    
    # Generate button
    if st.button("🎯 Generate Email", type="primary"):
        if not api_key:
            st.error("Please enter your Gemini API key in the sidebar!")
        elif not prompt:
            st.error("Please enter a prompt for email generation!")
        else:
            with st.spinner("Generating email..."):
                subject, body = generate_email(prompt, api_key)
                if subject:
                    st.session_state.email_subject = subject
                    st.session_state.generated_email = body
                    st.success("Email generated successfully!")
                else:
                    st.error(body)  # body contains error message in this case
    
    # Display generated email
    if st.session_state.generated_email:
        st.subheader("Generated Email Preview")
        
        # Editable subject
        st.session_state.email_subject = st.text_input(
            "Subject:",
            value=st.session_state.email_subject
        )
        
        # Editable email body
        st.session_state.generated_email = st.text_area(
            "Email Body:",
            value=st.session_state.generated_email,
            height=300
        )

with col2:
    st.header("📤 Send Email")
    
    if st.session_state.generated_email:
        # Recipient email input
        recipient_email = st.text_input(
            "Recipient Email Address:",
            placeholder="recipient@example.com"
        )
        
        # Additional recipients (optional)
        cc_recipients = st.text_input(
            "CC (optional, comma-separated):",
            placeholder="cc1@example.com, cc2@example.com"
        )
        
        # Send button
        if st.button("📧 Send Email", type="primary"):
            if not sender_email or not sender_password:
                st.error("Please configure your email settings in the sidebar!")
            elif not recipient_email:
                st.error("Please enter recipient email address!")
            else:
                with st.spinner("Sending email..."):
                    success, message = send_email(
                        sender_email,
                        sender_password,
                        recipient_email,
                        st.session_state.email_subject,
                        st.session_state.generated_email,
                        smtp_server,
                        smtp_port
                    )
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        
                        # Option to clear and start over
                        if st.button("✨ Generate Another Email"):
                            st.session_state.generated_email = ""
                            st.session_state.email_subject = ""
                            st.rerun()
                    else:
                        st.error(message)
                        if "Gmail" in smtp_provider:
                            st.info("💡 Tip: Make sure you're using an App Password, not your regular Gmail password. You can generate one in your Google Account settings under Security > 2-Step Verification > App passwords.")
    else:
        st.info("👈 Generate an email first using the form on the left")

# Footer
st.divider()
st.markdown("""
    ### 📚 Instructions:
    1. **Configure API Key**: Add your Google Gemini API key in the sidebar
    2. **Setup Email**: Configure your email settings (use App Passwords for Gmail/Yahoo)
    3. **Generate Email**: Enter a prompt and click Generate
    4. **Review & Edit**: Review the generated email and edit if needed
    5. **Send**: Enter recipient email and click Send
    
    ### 🔒 Security Notes:
    - Never share your API keys or passwords
    - Use App Passwords instead of regular passwords for Gmail/Yahoo
    - Consider using environment variables for sensitive data
    
    ### 🔑 Getting Gemini API Key:
    1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Sign in with your Google account
    3. Click "Create API Key"
    4. Copy the key and add it to the app
""")
