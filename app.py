import streamlit as st
import sqlite3
import os
from helper import generate, extract_text_from_pdf
from pathlib import Path

def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect('resumes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS resumes
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         filename TEXT,
         experience TEXT,
         skills TEXT,
         contact_details TEXT,
         upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

def save_to_db(filename, analysis_result):
    """Save the analysis results to database"""
    conn = sqlite3.connect('resumes.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO resumes (filename, experience, skills, contact_details)
        VALUES (?, ?, ?, ?)
    ''', (filename, analysis_result['experience'], analysis_result['skills'], analysis_result['contact_details']))
    conn.commit()
    conn.close()

def parse_analysis_result(text):
    """Parse the AI output into structured format"""
    sections = {'experience': '', 'skills': '', 'contact_details': ''}
    current_section = None
    
    for line in text.split('\n'):
        line = line.strip()
        if line.lower().startswith('- experience'):
            current_section = 'experience'
        elif line.lower().startswith('- skills'):
            current_section = 'skills'
        elif line.lower().startswith('- contact'):
            current_section = 'contact_details'
        elif line and current_section:
            sections[current_section] += line + '\n'
    print(sections)
    return sections

def user_interface():
    st.title("Resume Parser - User Interface")
    st.write("Upload a resume PDF to extract key information")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        if st.button("Analyze Resume"):
            with st.spinner("Extracting information..."):
                prompt = '''
                Always start answering by saying hello there
                    You are an advanced resume screening assistant. Extract and summarize the candidate's professional experience and key skills from the following resume.
Provide the output in the following format:

Experience Summary: List the most relevant roles, durations, and key achievements.
Key Skills: Highlight the candidate's technical, interpersonal, and domain-specific skills.
Ensure the summary is concise, focused on the recruiter's perspective, and easy to scan. Use bullet points for clarity.

Input Resume:
[Insert the resume text here]

Output:
Experience Summary:

[Role, Duration, Key Achievement]
[Role, Duration, Key Achievement]
Key Skills:

[Skill 1, Skill 2, Skill 3, ...]

Remember:

Be concise and specific
Focus on quantifiable achievements when available
Highlight skills that match current industry trends
Flag any potential red flags or gaps in experience

Give a score according to the experience within the range of 0 to 100. After the score, write a critic in 5 to 10 short points about the resume. 
After that give 5 suggestions to improve the resume score.
                '''
                
                text = extract_text_from_pdf("temp_resume.pdf")
                result = generate(prompt + text)
                
                st.subheader("Analysis Results")
                st.write(result)

def admin_interface():
    st.title("Resume Parser - Admin Interface")
    st.write("Upload multiple resumes for batch processing and storage")

    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        if st.button("Process and Store Resumes"):
            progress_bar = st.progress(0)
            for i, uploaded_file in enumerate(uploaded_files):
                with st.spinner(f'Processing {uploaded_file.name}...'):
                    # Save uploaded file
                    temp_path = f"temp_resume_{i}.pdf"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    # Process resume
                    prompt = '''Always start answering by saying hello there
                    You are an advanced resume screening assistant. Extract and summarize the candidate's professional experience and key skills from the following resume.
Provide the output in the following format:

Experience Summary: List the most relevant roles, durations, and key achievements.
Key Skills: Highlight the candidate's technical, interpersonal, and domain-specific skills.
Ensure the summary is concise, focused on the recruiter's perspective, and easy to scan. Use bullet points for clarity.

Input Resume:
[Insert the resume text here]

Output:
Experience Summary:

[Role, Duration, Key Achievement]
[Role, Duration, Key Achievement]
Key Skills:

[Skill 1, Skill 2, Skill 3, ...]

Remember:

Be concise and specific
Focus on quantifiable achievements when available
Highlight skills that match current industry trends
Flag any potential red flags or gaps in experience

Give a score according to the experience within the range of 0 to 100
                    '''
                    
                    text = extract_text_from_pdf(temp_path)
                    result = generate(prompt + text)
                    
                    # Parse and store results
                    parsed_result = parse_analysis_result(result)
                    save_to_db(uploaded_file.name, parsed_result)
                    
                    # Update progress
                    progress_bar.progress((i + 1)/len(uploaded_files))
                    
                    # Clean up temp file
                    os.remove(temp_path)
            
            st.success("All resumes processed and stored in database!")
        
        # Display database contents
        if st.button("View Database Contents"):
            conn = sqlite3.connect('resumes.db')
            c = conn.cursor()
            c.execute('SELECT filename, experience, skills, contact_details, upload_date FROM resumes')
            rows = c.fetchall()
            conn.close()
            
            if rows:
                st.subheader("Stored Resumes")
                for row in rows:
                    with st.expander(f"Resume: {row[0]} (Uploaded: {row[4]})"):
                        st.write("**Experience:**")
                        st.write(row[1])
                        st.write("**Skills:**")
                        st.write(row[2])
                        st.write("**Contact Details:**")
                        st.write(row[3])

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Interface", ["User", "Admin"])
    
    # Initialize database
    init_db()
    
    if page == "User":
        user_interface()
    else:
        admin_interface()

if __name__ == "__main__":
    main()