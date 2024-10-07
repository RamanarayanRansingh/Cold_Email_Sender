import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text, extract_emails
from gmail_sender import authenticate_gmail, send_email
import os

# Initialize Chain and Portfolio objects
chain = Chain()
portfolio = Portfolio()

# --- UI Styling ---
st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    
    body {
        font-family: 'Poppins', sans-serif;   
        background-color: #212529; /* Dark background */
        color: #E9ECEF; /* Light text for contrast */
    }
    .main {
        background-color: #282C34; /* Slightly lighter dark background for content area */
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    .stButton>button {
        background-color: #0062CC; 
        color: white;
        padding: 0.9rem 1.6rem;
        border: none;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #004BB5; 
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
    }
    .stTextInput>div>div>input {
        border: 2px solid #0062CC; 
        padding: 0.9rem;
        border-radius: 8px;
        font-size: 1rem;
        background-color: #FAFBFC; 
        color: #1C1E21;
        caret-color: #0062CC; /* Set cursor color to blue */
    }

    /* Heading styles */
    h1, h2, h3, h4, h5, h6 {
        color: #0062CC; /* Blue color for headings */
        font-weight: 700;
    }
    
    h1 {
        font-size: 3rem; /* Increase font size for main heading */
    }

    h2 {
        font-size: 2.2rem; /* Adjusted size for job role */
        color: #0062CC !important; /* Ensure job role title is blue */
    }

    .job-details {
        background-color: #F8F9FA; /* Lighter grey for job details */
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-left: 6px solid #0062CC; 
    }
    .job-details p {
        color: #343A40; /* Slightly darker text for readability */
        font-weight: 400;
    }
    .stAlert {
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    .stSuccess {
        background-color: #28A745; 
        color: white;
        border: 1px solid #218838; 
    }
    .stWarning {
        background-color: #FFC107; 
        color: white;
        border: 1px solid #FFA000;
    }
    .stInfo {
        background-color: #17A2B8; 
        color: white;
        border: 1px solid #138496;
    }
    .error-message {
        background-color: #DC3545;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-family: 'Poppins', sans-serif;
        border: 1px solid #C82333;
    }
    .stTextArea textarea {
        border: 2px solid #0062CC; 
        border-radius: 8px;
        padding: 1rem;
        font-size: 1rem;
        background-color: #F8F9FA; /* Lighter grey background similar to job role section */
        color: #1C1E21; /* Darker text for readability */
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* Slight shadow for depth */
        caret-color: #0062CC; /* Set cursor color to blue */
    }
    .found-emails {
        color: #0062CC; 
        font-weight: 600;
        font-size: 1.1rem;
    }
    .recipient-email {
        font-size: 1rem;
        color: #1C1E21;
    }
    /* More specific spinner text fix */
    .stSpinner .spinner-container .spinner-text { 
        color: #004085 !important; /* Darker blue for better visibility */
        font-weight: 600;
        font-size: 1.1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- App Content ---
st.markdown(
    """
    <div class="main">
        <h1>📧 Cold Email Generator</h1>
        <h3>Generate personalized cold emails for job postings in seconds!</h3>
        <p>Just enter the URL of the job posting below.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Job URL Input
url_input = st.text_input("🔗 Job Posting URL", value="")

# Use session state to store the generated email
if 'generated_email' not in st.session_state:
    st.session_state.generated_email = ""

# Use session state to store the job analysis results
if 'job_analyzed' not in st.session_state:
    st.session_state.job_analyzed = False

if 'jobs' not in st.session_state:
    st.session_state.jobs = []

if 'raw_data' not in st.session_state:
    st.session_state.raw_data = ""

submit_button = st.button("🚀 Analyze Job Posting")

if submit_button and url_input:
    with st.spinner("⏳ Analyzing Job Posting..."):
        try:
            # Set the USER_AGENT environment variable
            os.environ[
                "USER_AGENT"
            ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"

            loader = WebBaseLoader([url_input])
            st.session_state.raw_data = loader.load().pop().page_content
            cleaned_data = clean_text(st.session_state.raw_data)

            # Extract and store job details
            st.session_state.jobs = chain.extract_jobs(cleaned_data)
            st.session_state.job_analyzed = True
        except Exception as e:
            st.markdown(f'<div class="error-message">❌ An error occurred: {str(e)}</div>', unsafe_allow_html=True)

if st.session_state.job_analyzed:
    if not st.session_state.jobs:
        st.markdown('<div class="stWarning">🔍 No job information found in the provided URL.</div>', unsafe_allow_html=True)
    else:
        for job in st.session_state.jobs:
            role = job.get("role", "N/A")
            skills = job.get("skills", [])

            st.markdown(
                f"""
                <div class='job-details'>
                    <h2>Job Role: {role}</h2>
                    <p><b>Required Skills:</b> {', '.join(skills)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

             # Generate Cold Email (only if not already generated)
            if not st.session_state.generated_email: 
                portfolio.load_portfolio()
                links = portfolio.query_links(skills)
                st.session_state.generated_email = chain.write_mail(job, links) 

            st.subheader("✉️ Edit and Send Your Cold Email:")
            email_editor = st.text_area(
                "Edit the email below:", 
                value=st.session_state.generated_email, 
                height=300
            )

            # Email Sending
            emails = extract_emails(st.session_state.raw_data)
            if emails:
                st.markdown(f'<div class="found-emails">🔍 Found the following email addresses: {", ".join(emails)}</div>', unsafe_allow_html=True)
                recipient_email = st.text_input(
                    "Recipient's Email Address",
                    value=emails[0] if emails else "",
                    key="recipient"
                )
            else:
                st.markdown('<div class="stWarning">⚠️ No email addresses found in the job posting. Please enter the recipient\'s email manually.</div>', unsafe_allow_html=True)
                recipient_email = st.text_input("Recipient's Email Address", key="recipient")

            if st.button("📤 Send Email") and recipient_email:
                with st.spinner("Sending email..."):
                    try:
                        service = authenticate_gmail()
                        send_email(
                            service,
                            recipient_email,
                            f"Job Application for {role}",
                            email_editor,
                        )
                        st.markdown('<div class="stSuccess">✅ Email sent successfully!</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="error-message">❌ Failed to send email: {str(e)}</div>', unsafe_allow_html=True)

