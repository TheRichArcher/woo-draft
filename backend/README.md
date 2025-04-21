# Woo-Draft Backend

## Local Development Setup

### 1. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and fill in the required values. At minimum, ensure all email-related variables are set correctly to avoid startup errors. For FastAPI-Mail, you must set:
- MAIL_STARTTLS (true/false)
- MAIL_SSL_TLS (true/false)

### 4. Start the Backend Server
From the `