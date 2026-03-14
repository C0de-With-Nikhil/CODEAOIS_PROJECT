import base64
import smtplib
from email.mime.text import MIMEText

# --- PRIVATE SECURE AUTHENTICATION MODULE ---
_E = b'Y2xpY29kZWFvaXNAZ21haWwsY29t' 
_P = b'dXhqaiBnY3BlIHlnZm4gYnN3eg====' 

def get_secure_credentials():
    """Decodes and returns the bot credentials at runtime."""
    try:
        # Note: I noticed a comma in your Base64 email string (Y2xp...Y29t). 
        # If it fails, check if the encoded string used a '.' instead of a ','
        email = base64.b64decode(_E).decode('utf-8').replace(',', '.')
        password = base64.b64decode(_P).decode('utf-8')
        return email, password
    except Exception:
        return None, None

def send_real_otp(receiver_email, otp_code):
    """Sends a REAL email using the decoded Base64 credentials."""
    sender_email, sender_password = get_secure_credentials()

    if not sender_email or not sender_password:
        return False

    msg = MIMEText(
        f"Hello!\n\n"
        f"Your CodeAOIS secure login verification code is: {otp_code}\n\n"
        f"This code will sync your global history from the cloud.\n\n"
        f"Welcome to the OS.\n- The CodeAOIS Team"
    )
    msg['Subject'] = 'CodeAOIS Secure Login Verification'
    msg['From'] = f"CodeAOIS Security <{sender_email}>"
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [receiver_email], msg.as_string())
        return True
    except Exception:
        return False