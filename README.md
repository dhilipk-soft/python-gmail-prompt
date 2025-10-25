# AI Email Generator & Sender (Gemini AI)

A Streamlit application that uses Google's Gemini AI to generate professional emails based on prompts and automatically sends them via SMTP.

## Features

- 🤖 **Gemini AI-Powered Email Generation**: Uses Google's Gemini Pro model to create professional emails
- ✉️ **Automatic Email Sending**: Send generated emails directly from the app
- ✏️ **Email Editing**: Review and edit generated emails before sending
- 🔐 **Secure Configuration**: Support for environment variables and app passwords
- 📧 **Multiple Email Providers**: Works with Gmail, Outlook, Yahoo, and custom SMTP servers
- 🆓 **Free AI API**: Gemini AI offers a generous free tier

## Prerequisites

- Python 3.7 or higher
- Google Gemini API key (free)
- Email account with SMTP access (Gmail, Outlook, Yahoo, etc.)

## Installation

1. **Clone or download this project**

2. **Install required packages:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables (optional but recommended):**

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` file and add your credentials:
```
GEMINI_API_KEY=your_gemini_api_key_here
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password_here
```

## Configuration

### Google Gemini API Key (Free!)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key" button
4. Copy the generated API key
5. Add it to the app or `.env` file

**Note**: Gemini AI offers a generous free tier with:
- 60 requests per minute
- No credit card required
- Free access to Gemini Pro model

### Email Setup

#### For Gmail:
1. Enable 2-Factor Authentication in your Google Account
2. Generate an App Password:
   - Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and your device
   - Copy the generated password
3. Use this App Password in the application (NOT your regular Gmail password)

#### For Yahoo:
1. Enable 2-Factor Authentication
2. Generate an App Password at [Yahoo Security](https://login.yahoo.com/account/security)
3. Use the App Password in the application

#### For Outlook/Hotmail:
- If 2FA is disabled: Use your regular password
- If 2FA is enabled: Generate an app password in account settings

## Usage

1. **Start the application:**
```bash
streamlit run email_generator_app.py
```

2. **Configure settings in the sidebar:**
   - Enter your Gemini API key
   - Select your email provider
   - Enter your email credentials

3. **Generate an email:**
   - Enter a prompt (e.g., "Write a leave request for 2 days")
   - Click "Generate Email"
   - Review and edit the generated email if needed

4. **Send the email:**
   - Enter recipient email address
   - Optionally add CC recipients
   - Click "Send Email"

## Example Prompts

- "Write a professional leave request email for 2 days due to personal reasons"
- "Create a job application email for a software developer position"
- "Draft a meeting request email for next Tuesday at 2 PM"
- "Write a follow-up email after a job interview"
- "Create an apology email for missing a deadline"
- "Write a resignation letter with 2 weeks notice"

## Security Best Practices

1. **Never commit credentials to version control**
   - Add `.env` to your `.gitignore` file
   - Use environment variables for all sensitive data

2. **Use App Passwords**
   - Don't use your regular email password
   - Generate app-specific passwords for better security

3. **Protect your API keys**
   - Don't share your Gemini API key
   - Regenerate keys if compromised
   - Monitor your API usage regularly

4. **HTTPS/TLS**
   - The app uses TLS encryption for email sending
   - Ensure your SMTP settings use secure ports (587 for TLS)

## Troubleshooting

### Email sending fails:
- Verify you're using an App Password (not regular password) for Gmail/Yahoo
- Check if "Less secure app access" is needed (not recommended)
- Ensure 2FA is properly configured
- Verify SMTP settings (server and port)

### Gemini API errors:
- Check if API key is valid
- Verify you haven't exceeded the free tier limits (60 requests/minute)
- Check Google AI Studio for service status
- Try regenerating your API key if issues persist

### Connection issues:
- Check your internet connection
- Verify firewall settings aren't blocking SMTP ports
- Try different SMTP ports (587, 465, 25)

## Cost Considerations

- **Gemini AI is FREE** with generous limits:
  - 60 requests per minute
  - No credit card required
  - Free access to Gemini Pro model
- Monitor your usage at [Google AI Studio](https://makersuite.google.com/app/apikey)

## Future Enhancements

Potential improvements for the application:
- Email templates for common scenarios
- Multiple recipient support with BCC
- Email scheduling
- Attachment support
- Email history and drafts
- Integration with email APIs (SendGrid, Mailgun)
- Support for HTML formatted emails

## License

This project is provided as-is for educational and personal use.

## Disclaimer

This application handles sensitive information (API keys and passwords). Always follow security best practices and never share your credentials.
