from openai import OpenAI
import os
import io
import streamlit as st
from PyPDF2 import PdfReader
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

logging.info("Starting Resume Critique Application")
load_dotenv()
st.set_page_config(page_title="Resume Critique",page_icon="🧪")

st.title("🧪 Resume Critique Application")
st.markdown("""Upload your resume in PDF format, and receive constructive feedback to enhance its effectiveness.""")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()
uploaded_file=st.file_uploader("Upload your Resume (PDF nd Text files supported only)",type=["pdf","txt"])
job_role=st.text_input("Enter the Job Role you are targeting (e.g., Software Engineer, Data Scientist):")
analyze=st.button("Get Resume Feedback")


def extract_text_from_pdf(file):
    reader=PdfReader(file)
    text=""
    for page in reader.pages:
        text+=page.extract_text()+ "\n"
    return text

def extract_text_from_file(file):
    if "pdf" in file.type:
        return extract_text_from_pdf(io.BytesIO(file.read()))
    
    return file.read().decode('utf-8')

def get_resume_feedback():
    if not uploaded_file:
        st.error("Please Upload your resume file")
        return
    if not job_role:
        st.error("Please enter the job role you are targeting")
        return
    with st.spinner("Analyzing resume..."):
        resume_text=extract_text_from_file(uploaded_file)
        if not resume_text.strip():
            st.error("The uploaded resume file is empty or could not be read.")
            return
        prompt = f"Please analyze this resume and provide constructive feedback. Focus on: (1) content clarity and impact, (2) skills presentation, (3) experience descriptions, and (4) specific improvements for {job_role if job_role else 'general job applications'}. Resume content:\n{resume_text}\nProvide your analysis in a clear, structured format with specific recommendations."
        try:
            client=OpenAI(api_key=OPENAI_API_KEY)
            response=client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":"You are a helpful assistant that provides detailed resume critiques."},
                    {"role":"user","content":prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            st.success("Resume analysis complete!")
            feedback=response.choices[0].message.content
            st.markdown("### Analysis and Results:")
            st.markdown(feedback)
        except Exception as e:
            logging.error(f"Error during OpenAI API call: {e}")
            st.error("An error occurred while processing your request. Please try again later.")


if analyze:
    try:
        get_resume_feedback()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        st.error("An unexpected error occurred. Please try again later.")