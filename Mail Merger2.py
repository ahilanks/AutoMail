import pandas as pd
import fitz
import google.generativeai as genai

genai.configure(api_key="AIzaSyDSLGbQh5NR-MBLVCIyezAeRYrNRfsBZbA")
model = genai.GenerativeModel("gemini-1.5-flash")

people = pd.read_csv('/Users/ahilankaruppusami/Downloads/Mail Merge Test 2 - Sheet1 (2).csv')
resume_path = "/Users/ahilankaruppusami/Downloads/Karuppusami_Ahilan--Resume.pdf"

# Extract resume_text from all pages
with fitz.open(resume_path) as doc:
    resume_text = ''.join(page.get_text() for page in doc)

def findEmail(people):
    # Split 'Name' into 'FirstName' and 'LastName'
    print(people['Name'].str.split().to_list())
    people[['FirstName', 'LastName']] = people['Name'].str.split()
    
    # Generate emails (replace with your actual email generation logic)
    emails = []
    for i, row in people.iterrows():
        email = f"{row['FirstName']}.{row['LastName']}@{row['Company'].replace(' ', '').lower()}.com"
        emails.append(email)
    
    people['Emails'] = emails

def writeEmail(df):
    emails = []
    for _, person in df.iterrows():
        prompt = f"""
        Generate a personalized email requesting a chat with:
        
        Recipient: {person.to_dict()}
        
        Using relevant details from this resume:
        {resume_text}
        
        The email should be professional, concise, and highlight relevant connections 
        between the resume and the recipient's background or company. Do not include any 
        brackets or fill in the blanks. Instead assume something specific based on the interest
        from the resume.

        Do not include the Subject line.

        Start with Hi <Name>,
        """
        
        response = model.generate_content(prompt)
        emails.append(response.text)
    df['Email Content'] = emails

findEmail(people)
writeEmail(people)









