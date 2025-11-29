import os
import base64
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_gmail_service():
    """Authenticate and return Gmail API service."""
    creds = None

    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080,
                                         prompt='consent',
                                         access_type='offline')

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


def scrape_professor_website(url):
    """Scrape professor's website and clean the content."""
    loader = WebBaseLoader(url)
    docs = loader.load()
    page_content = docs[0].page_content.replace('\n', ' ')
    return page_content


def generate_email_and_extract_info(page_content, resume_content, llm):
    """Use LLM to extract professor's email and generate personalized email."""

    # Extract professor's email
    email_extraction_prompt = f"""
From the following professor's website content, extract the professor's email address.
Only return the email address, nothing else.

Website Content:
{page_content}
"""

    email_response = llm.invoke(email_extraction_prompt)
    professor_email = email_response.content.strip()

    # Generate personalized email
    email_generation_prompt = f"""
You are helping a student write a professional email to a professor to express interest in their research.

Professor's Website Content:
{page_content}

Student's Resume:
{resume_content}

Write a concise, professional email (150-200 words) that:
1. First paragraph shows genuine interest in the professor's research
2. Second paragraph highlights relevant experience from the student's resume that aligns with the professor's work
3. Third paragraph Expresses interest in potential research opportunities or collaboration next semester(Spring 2026) and says you have attached your resume for their reference and would love to schedule a meeting to discuss further.
4. Is respectful and professional in tone

Only return the email body text, without subject line.
"""

    email_body_response = llm.invoke(email_generation_prompt)
    email_body = email_body_response.content.strip()

    return professor_email, email_body


def send_email_oauth(service, sender_email, recipient_email, subject, body, attachment_path=None):
    """Send email using Gmail API with OAuth2."""

    # Create multipart message
    message = MIMEMultipart()
    message['to'] = recipient_email
    message['from'] = sender_email
    message['subject'] = subject

    # Add body
    message.attach(MIMEText(body, 'plain'))

    # Add attachment if provided
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={os.path.basename(attachment_path)}'
        )
        message.attach(part)

    # Encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    try:
        message_body = {'raw': raw_message}
        sent_message = service.users().messages().send(
            userId='me', body=message_body).execute()

        return True, sent_message['id']

    except Exception as e:
        return False, str(e)


def apply_custom_css():
    """Apply custom CSS for beautiful styling."""
    st.markdown("""
        <style>
        /* Main app styling */
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        /* Card styling */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        /* Custom container styling */
        .auth-container {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            margin: 0 auto;
            margin-top: 5rem;
        }

        .main-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            margin-top: 2rem;
        }

        /* Title styling */
        h1 {
            color: #667eea;
            text-align: center;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        h2 {
            color: #764ba2;
            font-weight: 600;
        }

        h3 {
            color: #667eea;
            font-weight: 600;
        }

        /* Button styling */
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            width: 100%;
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }

        /* Input styling */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            padding: 0.75rem;
            transition: border-color 0.3s ease;
        }

        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }

        /* File uploader styling */
        .uploadedFile {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
        }

        /* Success/Error messages */
        .stSuccess, .stError, .stInfo {
            border-radius: 10px;
            padding: 1rem;
        }

        /* Center text */
        .center-text {
            text-align: center;
        }

        /* Icon styling */
        .big-icon {
            font-size: 4rem;
            text-align: center;
            margin-bottom: 1rem;
        }

        /* Divider */
        hr {
            margin: 2rem 0;
            border: none;
            border-top: 2px solid #f0f0f0;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }

        [data-testid="stSidebar"] .stMarkdown {
            color: white;
        }

        /* Status indicator */
        .status-badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            margin: 0.5rem 0;
        }

        .status-success {
            background: #d4edda;
            color: #155724;
        }

        .status-pending {
            background: #fff3cd;
            color: #856404;
        }
        </style>
    """, unsafe_allow_html=True)


def authentication_page():
    """Display authentication page."""
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)

    st.markdown('<div class="big-icon">📧</div>', unsafe_allow_html=True)
    st.markdown('<h1>Professor Email Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="center-text" style="color: #666; margin-bottom: 2rem;">Generate personalized emails to professors with AI</p>', unsafe_allow_html=True)

    st.markdown("---")

    # Email input
    sender_email = st.text_input("📨 Your Email Address",
                                 placeholder="your.email@university.edu",
                                 key="sender_email_input")

    # OpenAI API Key
    openai_api_key = st.text_input("🔑 OpenAI API Key",
                                   type="password",
                                   placeholder="sk-...",
                                   value=os.getenv("OPENAI_API_KEY", ""),
                                   key="openai_key_input")

    st.markdown("<br>", unsafe_allow_html=True)

    # Resume upload
    st.markdown("### 📄 Upload Your Resume")

    col1, col2 = st.columns(2)

    with col1:
        resume_txt = st.file_uploader("Resume (TXT)", type=['txt'],
                                      help="Plain text version for AI processing")

    with col2:
        resume_pdf = st.file_uploader("Resume (PDF)", type=['pdf'],
                                     help="PDF version to attach to emails")

    st.markdown("<br>", unsafe_allow_html=True)

    # Gmail authentication button
    if st.button("🔐 Sign In with Gmail", type="primary"):
        if not sender_email:
            st.error("❌ Please enter your email address")
            return

        if not openai_api_key:
            st.error("❌ Please enter your OpenAI API key")
            return

        if not resume_txt or not resume_pdf:
            st.error("❌ Please upload both TXT and PDF versions of your resume")
            return

        with st.spinner("🔄 Authenticating with Gmail..."):
            try:
                # Save resume files
                with open("resume_temp.txt", "wb") as f:
                    f.write(resume_txt.getbuffer())

                with open("resume_temp.pdf", "wb") as f:
                    f.write(resume_pdf.getbuffer())

                # Authenticate Gmail
                service = get_gmail_service()

                # Store in session state
                st.session_state['authenticated'] = True
                st.session_state['gmail_service'] = service
                st.session_state['sender_email'] = sender_email
                st.session_state['openai_api_key'] = openai_api_key
                st.session_state['resume_txt_path'] = "resume_temp.txt"
                st.session_state['resume_pdf_path'] = "resume_temp.pdf"

                st.success("✅ Authentication successful!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Authentication failed: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)


def main_app():
    """Display main application after authentication."""

    # Sidebar
    with st.sidebar:
        st.markdown("### 👤 Account")
        st.markdown(f'<div class="status-badge status-success">✓ Signed in as {st.session_state["sender_email"]}</div>',
                   unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("### 📊 Status")
        if 'gmail_service' in st.session_state:
            st.markdown('<div class="status-badge status-success">✓ Gmail Connected</div>', unsafe_allow_html=True)

        if 'resume_txt_path' in st.session_state:
            st.markdown('<div class="status-badge status-success">✓ Resume Uploaded</div>', unsafe_allow_html=True)

        st.markdown("---")

        if st.button("🚪 Sign Out"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Main content
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.title("✨ Generate Professor Email")

    st.markdown("---")

    # Input section
    col1, col2 = st.columns([2, 1])

    with col1:
        professor_url = st.text_input("🌐 Professor's Website URL",
                                      placeholder="https://www.university.edu/professor",
                                      help="Enter the URL of the professor's webpage")

    with col2:
        subject = st.text_input("📬 Email Subject",
                               value="Interest in Research Opportunities")

    st.markdown("<br>", unsafe_allow_html=True)

    # Generate button
    if st.button("🎯 Generate Email", type="primary"):
        if not professor_url:
            st.error("❌ Please enter a professor's website URL")
            return

        try:
            # Initialize LLM
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                max_tokens=300,
                api_key=st.session_state['openai_api_key']
            )

            # Progress indicators
            progress_container = st.container()

            with progress_container:
                # Scrape professor's website
                with st.spinner("🔍 Analyzing professor's website..."):
                    page_content = scrape_professor_website(professor_url)
                st.success(f"✅ Scraped {len(page_content):,} characters")

                # Load resume
                with st.spinner("📄 Processing your resume..."):
                    with open(st.session_state['resume_txt_path'], 'r') as f:
                        resume_content = f.read()
                st.success("✅ Resume loaded")

                # Generate email
                with st.spinner("✨ Generating personalized email..."):
                    professor_email, email_body = generate_email_and_extract_info(
                        page_content, resume_content, llm
                    )
                st.success("✅ Email generated!")

            # Store in session state
            st.session_state['professor_email'] = professor_email
            st.session_state['email_body'] = email_body
            st.session_state['subject'] = subject

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # Display generated email
    if 'professor_email' in st.session_state and 'email_body' in st.session_state:
        st.markdown("---")
        st.markdown("### 📬 Generated Email Preview")

        # Email preview in a nice container
        with st.container():
            col1, col2 = st.columns([1, 3])

            with col1:
                st.markdown("**To:**")
                st.markdown("**Subject:**")

            with col2:
                st.markdown(f"`{st.session_state['professor_email']}`")
                st.markdown(f"`{st.session_state['subject']}`")

            st.markdown("<br>", unsafe_allow_html=True)

            # Editable email body
            edited_body = st.text_area("**Message:**",
                                       value=st.session_state['email_body'],
                                       height=300,
                                       help="You can edit the email before sending")

            st.session_state['email_body'] = edited_body

            st.markdown("<br>", unsafe_allow_html=True)

            # Send button
            col1, col2, col3 = st.columns([1, 1, 1])

            with col2:
                if st.button("📤 Send Email", type="primary", use_container_width=True):
                    with st.spinner("📨 Sending email..."):
                        success, result = send_email_oauth(
                            st.session_state['gmail_service'],
                            st.session_state['sender_email'],
                            st.session_state['professor_email'],
                            st.session_state['subject'],
                            st.session_state['email_body'],
                            st.session_state['resume_pdf_path']
                        )

                        if success:
                            st.success(f"✅ Email sent successfully!")
                            st.balloons()

                            # Clear the generated email from session
                            del st.session_state['professor_email']
                            del st.session_state['email_body']

                        else:
                            st.error(f"❌ Failed to send email: {result}")

    st.markdown('</div>', unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Professor Email Generator",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS
    apply_custom_css()

    # Check authentication state
    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
        authentication_page()
    else:
        main_app()


if __name__ == "__main__":
    main()
