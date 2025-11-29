# 📧 Professor Email Generator

A beautiful Streamlit web app that generates personalized emails to professors using AI, with Gmail OAuth integration.

## ✨ Features

- 🔐 **Gmail OAuth Authentication** - Secure email sending via Gmail API
- 🤖 **AI-Powered Email Generation** - Uses OpenAI GPT-4 to craft personalized emails
- 📄 **Resume Attachment** - Automatically attaches your resume to emails
- 🌐 **Professor Website Scraping** - Analyzes professor's webpage for personalized content
- 🎨 **Beautiful UI** - Modern gradient design with smooth animations
- ✏️ **Edit Before Sending** - Review and modify generated emails

## 🚀 Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client langchain-community langchain-openai streamlit beautifulsoup4 lxml
```

### 2. Set up Google Cloud OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the credentials JSON file
6. Save it as `credentials.json` in the project directory

### 3. Add Test Users (for CMU/SSO emails)

1. Go to [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
2. Under "Test users", click "ADD USERS"
3. Add your email address (e.g., `youremail@andrew.cmu.edu`)
4. Save

### 4. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy it for use in the app

## 📖 Usage

### Run the Streamlit App Locally

```bash
source venv/bin/activate
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. **Push to GitHub** (already done)

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository: `ajmehta11/professor-email-generator`
   - Main file path: `app.py`
   - Click "Deploy"

3. **Configure Secrets**
   - In your deployed app, go to Settings → Secrets
   - Add your OAuth credentials:

   ```toml
   [google_oauth]
   client_id = "YOUR_CLIENT_ID"
   client_secret = "YOUR_CLIENT_SECRET"
   ```

   - Get these values from your `credentials.json` file:
     - `client_id` = the value under `installed.client_id`
     - `client_secret` = the value under `installed.client_secret`

4. **Update OAuth Redirect URIs**
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Edit your OAuth 2.0 Client ID
   - Add authorized redirect URIs:
     - `http://localhost:8501`
     - `https://YOUR-APP-NAME.streamlit.app` (if needed)

5. **Make App Public** (Optional)
   - Go to [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
   - Click "PUBLISH APP" to allow anyone to use it
   - Or add specific test users

### Using the App

1. **Sign In**
   - Enter your email address
   - Enter your OpenAI API key
   - Upload your resume (TXT and PDF versions)
   - Click "Sign In with Gmail"

2. **Generate Email**
   - Enter professor's website URL
   - Enter email subject (or use default)
   - Click "Generate Email"

3. **Send**
   - Review and edit the generated email
   - Click "Send Email"

### Command Line Script

For command-line usage:

```bash
source venv/bin/activate
python3 send_professor_email_oauth.py
```

## 📁 Project Structure

```
emailer/
├── app.py                          # Streamlit web app
├── send_professor_email_oauth.py   # CLI email sender
├── credentials.json                # Google OAuth credentials (not in git)
├── token.json                      # OAuth token (auto-generated, not in git)
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🔒 Security Notes

- `credentials.json` and `token.json` are excluded from git
- Never commit API keys or credentials
- Keep your OpenAI API key secure

## 🛠️ Technologies

- **Streamlit** - Web framework
- **Google Gmail API** - Email sending
- **OpenAI GPT-4** - Email generation
- **LangChain** - LLM orchestration
- **BeautifulSoup** - Web scraping

## 📝 License

MIT License
