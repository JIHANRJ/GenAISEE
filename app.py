from dotenv import load_dotenv
load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text.strip().replace("\n", "")

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        ## Convert the PDF to image
        images = pdf2image.convert_from_bytes(uploaded_file.read())

        first_page = images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

## Streamlit App

st.set_page_config(page_title="ATS Resume Expert")
st.header("ResumeReviewer.ai")
input_text = st.text_area("Job Description: ", key="input")
uploaded_file1 = st.file_uploader("Upload the first resume(PDF)...", type=["pdf"])
uploaded_file2 = st.file_uploader("Upload the second resume(PDF)...", type=["pdf"])

submit1 = st.button("Tell Me About the Resume")
submit2 = st.button("How Can I Improve my Skills")
submit3 = st.button("Percentage match")
submit4 = st.button("Choose candidate")
submit5 = st.button("UpSkill")
submit6 = st.button("Candidate's Domain")

input_prompt1 = """
You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage and last final thoughts. Give percentage matches for skill, communication, experience, leadership, and overall percentage in a tabular format. 
"""

input_prompt4 = """
Given the above candidate resumes, you are supposed choose the best candidate based on match to the job description and tell why you choose the candidate, make sure you
explicitly name the candidate. Make sure the first Word of the response is the Candidates name. 
"""

input_prompt5 = """
Also give a description of why the candidate is choosen and what he/she can bring to the table in terms of the job description in under 50 words. Give percentage matches for skill, communication, experience, leadership, and overall percentage in a tabular format.
"""

input_prompt6 = """
Based on the provided job description provide actual links to course,
Let the output be of this format : 
here are some recommended courses and resources to upskill:
1. Course Name 1 - [Link 1]
2. Course Name 2 - [Link 2]
3. Course Name 3 - [Link 3]
"""

input_prompt7 = """
You are an experienced HR manager. Your task is to identify the domain or areas in which the resume is best suited for based on their resume given. Include info from the resume why they are good for that domain, Like for example if a candidate has worked with Googel GenAI, he's good for AI etc.stating the fact. 
The ouptut should be in tabluar format as in, like a  table, with a column consisting of related domains and another column consisting of percentage score and the total should add up to a hundered, there also should another column with info from th resume reassuring the percentage given per domain.
"""

if submit1:
    if uploaded_file1 is not None:
        pdf_content = input_pdf_setup(uploaded_file1)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume")

elif submit3:
    if uploaded_file1 is not None:
        pdf_content = input_pdf_setup(uploaded_file1)
        response = get_gemini_response(input_prompt3, pdf_content, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume")

elif submit2:
    if uploaded_file1 is not None:
        pdf_content = input_pdf_setup(uploaded_file1)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume")

elif submit4:
    if uploaded_file1 is not None and uploaded_file2 is not None:
        pdf_content1 = input_pdf_setup(uploaded_file1)
        pdf_content2 = input_pdf_setup(uploaded_file2)
        response1 = get_gemini_response(input_prompt4, pdf_content1, input_text)
        response2 = get_gemini_response(input_prompt4, pdf_content2, input_text)
        
        
        if response1 > response2:
            #chosen_candidate = "Candidate from the first resume"
            cand_name = get_gemini_response("Get the candidate name", pdf_content1, input_text)
            st.subheader("Chosen Candidate:")
            st.write(cand_name)
            description = get_gemini_response(input_prompt5,pdf_content1,input_text)
            st.write(description)
        else:
            cand_name = get_gemini_response("What is the candidate's name, return just the name please ", pdf_content2, input_text)
            st.subheader("Chosen Candidate:")
            st.write(cand_name)
            description = get_gemini_response(input_prompt5,pdf_content2,input_text)
            st.write(description)
        
    else:
        st.write("Please upload both resumes to compare")

if submit5:
    if input_text:
        pdf_content = input_pdf_setup(uploaded_file1)
        response = get_gemini_response(input_prompt6, pdf_content, prompt=input_text)
        courses = response.split("\n")
        st.subheader("Recommended Courses and Resources to Upskill:")
        for idx, course in enumerate(courses, start=1):
            link = f"https://example.com/course/{idx}"  # Replace with actual link generation logic
            st.write(f"{idx}. {course} - [{link}]")
    else:
        st.write("Please provide the job description to get recommended courses and resources.")

if submit6:
    if uploaded_file1 is not None:
        pdf_content = input_pdf_setup(uploaded_file1)
        input_text=" "
        response = get_gemini_response(input_prompt7, pdf_content, input_text)
        st.subheader("Candidate's Domain or Areas of Expertise:")
        st.write(response)
    else:
        st.write("Please upload the resume")
