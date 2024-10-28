import pandas as pd
import fitz
import google.generativeai as genai

genai.configure(api_key="AIzaSyDSLGbQh5NR-MBLVCIyezAeRYrNRfsBZbA")
model = genai.GenerativeModel("gemini-1.5-flash")


people = pd.read_csv('/Users/ahilankaruppusami/Downloads/Mail Merge Test - Sheet1.csv')
resume_path = "/Users/ahilankaruppusami/Downloads/Karuppusami_Ahilan--Resume.pdf"

# Extract resume_text from all pages
doc = fitz.open(resume_path)
resume_text = ""
for page_num in range(doc.page_count):
    page = doc.load_page(page_num)  # Load each page
    resume_text += page.get_resume_text()  # Extract resume_text
doc.close()

def findEmail(people):
    # Find all email addresses in the dataframe
    firstNames = people['Name'].str.split()[0].to_list()
    lastNames = people['Name'].str.split()[1].to_list()
    companies = people["Company"].to_list()
    emails = pd.Series()
    for i in range(len(firstNames)):
        #API call to get email address
        #email =  companies[i] firstNames[i] lastNames[i]
        emails.append()

    people["Emails"] = emails

def writeEmail(df):
    emails = pd.Series()
    for _, person in df.iterrows():
            prompt = f"""
            Generate a personalized email requesting a chat with:
            
            Recipient: {person.to_dict()}
            
            Using relevant details from this resume:
            {resume_text}
            
            The email should be professional, concise, and highlight relevant connections 
            between the resume and the recipient's background or company.
            """
            
            response = model.generate_content(prompt)
            emails.append(response)
    df["Emails"] = emails


findEmail(people)
writeEmail(people)
print(people)