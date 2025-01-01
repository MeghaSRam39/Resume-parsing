# # import streamlit as st
# # import pandas as pd
# # import base64, random
# # import time, datetime
# # import io, random
# # from streamlit_tags import st_tags
# # from PIL import Image
# # import pymysql 
# import os
# # import pafy
# # import plotly.express as px 
# # import nltk
# from dotenv import load_dotenv

# load_dotenv('.env')


# password = os.getenv('password')
# print(password)

# # nltk.download('stopwords')

# # def fetch_yt_video(link):
# #     video = pafy.new(link)
# #     return video.title


# #connect to mysql db
# connection = pymysql.connect(host = 'localhost', user = 'root', password = password, db = 'cv')
# cursor = connection.cursor()


import streamlit as st
import os
import PyPDF2
from pathlib import Path

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def analyze_resume(text):
    """
    Analyze the resume text and extract relevant information.
    This is a placeholder - replace with your actual analysis logic.
    """
    # This is where you'd put your actual analysis logic
    # For now, returning a simple structured output
    return {
        "Experience": [
            "• Position details would be listed here",
            "• Another position would be here"
        ],
        "Skills": [
            "• Extracted skills would be listed here",
            "• More skills would be here"
        ],
        "Contact Details": [
            "• Contact information would be listed here",
            "• More contact details would be here"
        ]
    }

def main():
    st.title("Resume Analyzer")
    st.write("Upload a PDF resume to extract key information")

    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Show the resume content
        with st.expander("Show Raw Text"):
            resume_text = extract_text_from_pdf(uploaded_file)
            st.text(resume_text)

        # Analyze button
        if st.button("Analyze Resume"):
            with st.spinner("Analyzing resume..."):
                # Get the analysis results
                results = analyze_resume(resume_text)

                # Display results in a nice format
                for section, items in results.items():
                    st.subheader(section)
                    for item in items:
                        st.write(item)

if __name__ == "__main__":
    main()