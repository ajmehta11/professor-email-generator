import re
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI


def scrape_professor_website(url):
    """Scrape professor's website and clean the content."""
    loader = WebBaseLoader(url)
    docs = loader.load()

    # Remove all newlines from page_content
    page_content = docs[0].page_content.replace('\n', ' ')

    return page_content


def load_resume(resume_path):
    """Load resume from file."""
    with open(resume_path, 'r') as f:
        resume_content = f.read()
    return resume_content


def generate_email_and_extract_info(page_content, resume_content, llm):
    """Use LLM to extract professor's email and generate personalized email."""

    # First, extract professor's email
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


def send_email(sender_email, sender_password, recipient_email, subject, body):
    """Send email using SMTP."""

    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Add body to email
    msg.attach(MIMEText(body, 'plain'))

    # Send email using Gmail SMTP
    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        # Login
        server.login(sender_email, sender_password)

        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)

        # Close connection
        server.quit()

        print(f"Email successfully sent to {recipient_email}")
        return True

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


def main():
    # Configuration
    professor_url = "https://www.synergylabs.org/yuvraj/"
    resume_path = "Aryan_Mehta_Resume.txt"
    sender_email = "ajmehta@andrew.cmu.edu"

    # Initialize LLM - API key from environment variable
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=300,  # Increased for email generation
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Step 1: Scrape professor's website
    print("Scraping professor's website...")
    page_content = scrape_professor_website(professor_url)
    print(f"Scraped {len(page_content)} characters")

    # Step 2: Load resume
    print("Loading resume...")
    resume_content = load_resume(resume_path)

    # Step 3: Generate email and extract professor's email
    print("Generating personalized email and extracting professor's email...")
    professor_email, email_body = generate_email_and_extract_info(
        page_content, resume_content, llm
    )

    print(f"\nProfessor's Email: {professor_email}")
    print(f"\nGenerated Email:\n{email_body}")

    # Step 4: Send email
    subject = "Interest in Research Opportunities"

    # Get password from environment variable or prompt
    sender_password = os.getenv("EMAIL_PASSWORD")
    if not sender_password:
        sender_password = input("\nEnter your email password or app-specific password: ")

    send_confirmation = input(f"\nSend email to {professor_email}? (yes/no): ")

    if send_confirmation.lower() == 'yes':
        # For CMU email, you might need to modify the SMTP settings
        # This example uses Gmail. Adjust accordingly for CMU's email system
        send_email(sender_email, sender_password, professor_email, subject, email_body)
    else:
        print("Email not sent.")


if __name__ == "__main__":
    main()
