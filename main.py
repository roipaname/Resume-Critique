import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Resume Critique",page_icon=":briefcase:",layout="centered")
st.title("AI Resume Critique Tool")

st.markdown("Upload Resume and get AI-powered feedback to enhance your job application.")

OPEN_API_KEY=os.getenv("OPENAI_API_KEY")
uploaded_file=st.file_uploader("Upload your resume  (PDF format Only)",type=["pdf","txt"])
job_role= st.text_input("Enter the Job Role you are applying for:")

analyze=st.button("Analyze Resume")

def extract_text_from_pdf(file):
    pdf_reader=PyPDF2.PdfReader(file)
    text=""
    for page in pdf_reader.pages:
        text+=page.extract_text() + "\n"
    return text
def extract_text_from_file(uploaded_file):
    if uploaded_file.type=="application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode('utf-8')


if analyze and uploaded_file:
    st.write("Analyzing your resume...")
    try:
        file_content=extract_text_from_file(uploaded_file)
        if not file_content.strip():
            st.error("The file doesnt have any content")
            st.stop()

        prompt = f"""Please analyze this resume and provide constructive feedback. 
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience descriptions
        4. Specific improvements for {job_role if job_role else 'general job applications'}
        
        Resume content:
        {file_content}
        
        Please provide your analysis in a clear, structured format with specific recommendations."""
        client=OpenAI(api_key=OPEN_API_KEY)
        response=client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are an expert career coach and resume reviewer."},
                {"role":"user","content":prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        st.markdown("### AI Resume Feedback:")
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")
