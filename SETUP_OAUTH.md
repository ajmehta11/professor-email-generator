# Gmail OAuth Setup Guide

This guide helps you set up OAuth2 authentication to send emails without entering passwords.

## Setup Steps

### 0. Add CMU Email as "Send mail as" in Gmail

**IMPORTANT**: To send from `ajmehta@andrew.cmu.edu` while authenticating with `aryanmehta765@gmail.com`:

1. Go to Gmail: https://mail.google.com (login with `aryanmehta765@gmail.com`)
2. Click Settings (⚙️) → "See all settings"
3. Go to "Accounts and Import" tab
4. Under "Send mail as", click "Add another email address"
5. Enter:
   - Name: `Aryan Mehta`
   - Email: `ajmehta@andrew.cmu.edu`
   - Uncheck "Treat as an alias"
6. Click "Next Step" → "Send Verification"
7. Check your CMU email for verification code
8. Enter the code to verify
9. Set `ajmehta@andrew.cmu.edu` as default (optional)

Now Gmail API can send emails from your CMU address!

### 1. Install Required Packages
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client langchain langchain-community langchain-openai beautifulsoup4 lxml
```

### 2. Create Google Cloud Project & Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the Gmail API:
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 3. Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "+ CREATE CREDENTIALS" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: "Email Sender" (or any name)
   - User support email: `aryanmehta765@gmail.com`
   - Developer contact: `aryanmehta765@gmail.com`
   - Add `aryanmehta765@gmail.com` to "Test users"
   - Save and continue
4. Create OAuth Client ID:
   - Application type: "Desktop app"
   - Name: "Email Sender Client"
   - Click "Create"
5. Download the credentials:
   - Click the download button (⬇️) next to your OAuth 2.0 Client ID
   - Save as `credentials.json` in `/Users/aryanmehta/Documents/emailer/`

### 4. Set OpenAI API Key
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

Or add to your `.env` file and load it.

### 5. Run the Script

```bash
python send_professor_email_oauth.py
```

**First time only**: A browser window will open asking you to sign in and authorize the app. Once you approve:
- A `token.json` file will be created
- Future runs will use this token automatically (no login required!)

### 6. Troubleshooting

**"Access blocked: This app's request is invalid"**
- Make sure you added your email to "Test users" in OAuth consent screen

**Token expired**
- Delete `token.json` and run again to re-authenticate

**Gmail API not enabled**
- Go to Google Cloud Console and enable Gmail API for your project

## Files Created
- `credentials.json` - OAuth client credentials (download from Google Cloud)
- `token.json` - Auto-generated after first login (keeps you logged in)

## Security Notes
- Add `credentials.json` and `token.json` to `.gitignore`
- Never commit these files to version control
