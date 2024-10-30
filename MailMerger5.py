import pandas as pd
import fitz  # PyMuPDF
import anthropic
import requests
from typing import Tuple

# Replace with YOUR API Configuration
ANTHROPIC_API_KEY = "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"
HUNTER_API_KEY = "5449b736ce1b907212212856e16365e33fff5699"
HUNTER_API_URL = "https://api.hunter.io/v2/email-finder"

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def extract_personal_document_text(file_path: str) -> str:
    """
    Extract text content from all pages of a PDF about yourself or your organization.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Concatenated text from all pages
    """
    with fitz.open(file_path) as doc:
        return ''.join(page.get_text() for page in doc)

def split_full_name(full_name: str) -> Tuple[str, str]:
    """
    Split a full name into first name and last name.
    
    Args:
        full_name (str): Full name to split
        
    Returns:
        Tuple[str, str]: First name and last name
    """
    parts = full_name.split()
    first_name = parts[0]
    last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
    return pd.Series([first_name, last_name])

def get_email_from_hunter(first_name: str, last_name: str, company: str) -> Tuple[str, float]:
    """
    Fetch email address using Hunter.io API.
    
    Args:
        first_name (str): First name of the person
        last_name (str): Last name of the person
        company (str): Company domain name
        
    Returns:
        Tuple[str, float]: Email address and confidence score
    """
    params = {
        "domain": f"{company.replace(' ', '').lower()}.com",
        "first_name": first_name,
        "last_name": last_name,
        "api_key": HUNTER_API_KEY
    }
    
    response = requests.get(HUNTER_API_URL, params=params)
    
    if response.status_code == 200 and response.json().get("data"):
        print("Successfully retrieved email from Hunter.io")
        data = response.json()["data"]
        return data.get("email"), data.get("score", 0)
    
    # Fallback email generation
    print(f"Hunter.io API request failed with status code: {response.status_code}")
    fallback_email = f"{first_name}.{last_name}@{company.replace(' ', '').lower()}.com"
    return fallback_email, 0

def process_contacts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process contact information to add email addresses.
    
    Args:
        df (pd.DataFrame): DataFrame containing contact information
        
    Returns:
        pd.DataFrame: Updated DataFrame with email addresses
    """
    # Split names into first and last names
    df[['FirstName', 'LastName']] = df['Name'].apply(split_full_name)
    
    # Get emails for each contact
    emails_and_confidence = [
        get_email_from_hunter(row['FirstName'], row['LastName'], row['Company'])
        for _, row in df.iterrows()
    ]
    
    df['Email'] = [email for email, _ in emails_and_confidence]
    df['Email_Confidence'] = [confidence for _, confidence in emails_and_confidence]
    
    # Clean up temporary columns
    df = df.drop(['FirstName', 'LastName'], axis=1)
    return df

def generate_personalized_emails(df: pd.DataFrame, resume_text: str) -> pd.DataFrame:
    """
    Generate personalized emails for each contact using Claude API.
    
    Args:
        df (pd.DataFrame): DataFrame containing contact information
        resume_text (str): Text content from resume
        
    Returns:
        pd.DataFrame: Updated DataFrame with email content
    """
    email_contents = []
    
    for _, contact in df.iterrows():
        prompt = f"""
        Generate a personalized email requesting a chat with:
        
        Recipient: {contact.to_dict()}
        
        Using relevant details from this resume:
        {resume_text}
        
        The email should be professional, concise, and highlight relevant connections 
        between the resume and the recipient's background or company. Do not include any 
        brackets or fill in the blanks. Instead assume something specific based on the background 
        of the person and the interests from the resume.

        Do not include the Subject line.

        Start with Hi {contact['Name']},
        """
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )
        email_contents.append(response.content[0].text)
    
    df['Email_Content'] = email_contents
    return df

def main():
    # Replace with YOUR file paths
    contacts_path = '/Users/ahilankaruppusami/Downloads/Mail Merge Test - Sheet1.csv'
    resume_path = "/Users/ahilankaruppusami/Downloads/Karuppusami_Ahilan--Resume.pdf"
    output_path = "/Users/ahilankaruppusami/Coding_Projects/Mail Merging/Spreadsheets/my_data.xlsx"
    
    # Load and process data
    contacts_df = pd.read_csv(contacts_path)
    resume_text = extract_resume_text(resume_path)
    
    # Process contacts to get emails
    contacts_df = process_contacts(contacts_df)
    
    # Optionally generate personalized emails
    # contacts_df = generate_personalized_emails(contacts_df, resume_text)
    
    # Save results
    contacts_df.to_excel(output_path, index=False)

if __name__ == "__main__":
    main()