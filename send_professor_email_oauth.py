import os
import base64
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
            # Add redirect_uri explicitly to avoid invalid_request error
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


def load_resume(resume_path):
    """Load resume from file."""
    with open(resume_path, 'r') as f:
        resume_content = f.read()
    return resume_content


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

        print(f"Email successfully sent to {recipient_email}")
        print(f"Message ID: {sent_message['id']}")
        return True

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


def main():
    # Configuration
    professor_url = "https://www.synergylabs.org/yuvraj/"
    resume_path = "Aryan_Mehta_Resume.txt"
    resume_pdf_path = "Aryan_Mehta_Resume.pdf"
    sender_email = "ajmehta@andrew.cmu.edu"  # Can use alias if configured in Gmail

    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=300,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Step 1: Authenticate with Gmail (only first time, then uses saved token)
    print("Authenticating with Gmail...")
    service = get_gmail_service()
    print("Authentication successful!")

    # Step 2: Scrape professor's website
    print("\nScraping professor's website...")
    page_content = scrape_professor_website(professor_url)
    print(f"Scraped {len(page_content)} characters")

    # Step 3: Load resume
    print("Loading resume...")
    resume_content = load_resume(resume_path)

    # Step 4: Generate email and extract professor's email
    print("Generating personalized email and extracting professor's email...")
    professor_email, email_body = generate_email_and_extract_info(
        page_content, resume_content, llm
    )

    print(f"\nProfessor's Email: {professor_email}")
    print(f"\nGenerated Email:\n{email_body}")

    # Step 5: Send email
    subject = "Interest in Research Opportunities"

    send_confirmation = input(f"\nSend email to {professor_email}? (yes/no): ")

    if send_confirmation.lower() == 'yes':
        send_email_oauth(service, sender_email, professor_email, subject, email_body, resume_pdf_path)
    else:
        print("Email not sent.")


if __name__ == "__main__":
    main()
