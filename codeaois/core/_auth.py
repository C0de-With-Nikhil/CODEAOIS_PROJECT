import base64

# --- PRIVATE SECURE AUTHENTICATION MODULE ---
# These are Base64 encoded to prevent simple bot scraping on GitHub.
# REMINDER: ONLY use a dummy "Bot" Gmail account for this, NEVER your personal email!

_E = b'Y2xpY29kZWFvaXNAZ21haWwsY29t' # Replace this string with your encoded bot email
_P = b'dXhqaiBnY3BlIHlnZm4gYnN3eg====' # Replace this string with your encoded app password

def get_secure_credentials():
    """Decodes and returns the bot credentials at runtime."""
    try:
        email = base64.b64decode(_E).decode('utf-8')
        password = base64.b64decode(_P).decode('utf-8')
        return email, password
    except Exception:
        return None, None