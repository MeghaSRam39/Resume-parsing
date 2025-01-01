import streamlit as st
from helper import generate, extract_text_from_pdf

def main():
    st.title("Resume Parser")
    st.write("Upload a resume PDF to extract key information")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        # Create a temporary file to store the uploaded PDF
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        if st.button("Analyze Resume"):
            with st.spinner("Extracting information..."):
                # Use your helper functions
                prompt = '''
                You will be given the text extracted form a resume. You have to properly extract the relevant information in the following format.
                - Experience
                - Skills
                - Contact details
                '''
                
                # Extract text using your function
                text = extract_text_from_pdf("temp_resume.pdf")
                
                # Generate analysis using your function
                result = generate(prompt + text)
                
                # Display results
                st.subheader("Analysis Results")
                st.write(result)

if __name__ == "__main__":
    main()