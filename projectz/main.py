import streamlit as st
import requests
from fpdf import FPDF
import io

# === CONFIGURATION ===
API_KEY = "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" 
MODEL = "llama3-70b-8192"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# === FUNCTION TO CALL GROQ API ===
def get_resume_from_llama(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional resume assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"Groq API Error: {response.status_code} {response.text}")

# === FUNCTION TO CONVERT TEXT TO PDF ===
def text_to_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf_output = pdf.output(dest="S").encode("latin1")  # Return PDF as string and encode
    return io.BytesIO(pdf_output)

# === STREAMLIT UI ===
st.set_page_config(page_title="Resume Builder", page_icon="📝")
st.title("AI Resume Builder ")

# === Initialize session state for resume ===
if "generated_resume" not in st.session_state:
    st.session_state.generated_resume = None

# === FORM ===
with st.form("resume_form"):
    st.subheader("Enter Your Details")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    linkedin = st.text_input("LinkedIn URL")
    github = st.text_input("GitHub URL")
    skills = st.text_area("Technical Skills (comma separated)")
    projects = st.text_area("Projects (titles only)")
    experience = st.text_area("Experience / Internships")
    education = st.text_area("Education")

    submitted = st.form_submit_button("Generate Resume")

# === AFTER FORM SUBMISSION ===
if submitted:
    with st.spinner("Generating your resume..."):
        try:
            prompt = f"""
            Create a professional resume in plain text based on the following details:
            Name: {name}
            Email: {email}
            Phone: {phone}
            LinkedIn: {linkedin}
            GitHub: {github}
            Skills: {skills}
            Projects: {projects}
            Experience: {experience}
            Education: {education}

            Use a clean format with clearly marked sections for Summary, Skills, Projects, Experience, and Education.
            Keep the tone professional and suitable for job applications.
            """
            resume_text = get_resume_from_llama(prompt)
            st.session_state.generated_resume = resume_text
            st.success("✅ Resume generated successfully!")

        except Exception as e:
            st.error(f"❌ Error: {e}")

# === SHOW RESULT & PDF DOWNLOAD ===
if st.session_state.generated_resume:
    resume_text = st.session_state.generated_resume
    st.text_area("🧾 Resume Preview", value=resume_text, height=500)

    pdf_data = text_to_pdf(resume_text)
    st.download_button(
        label="📄 Download Resume as PDF",
        data=pdf_data,
        file_name="resume_generated.pdf",
        mime="application/pdf"
    )
