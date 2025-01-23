import streamlit as st
import sqlite3
import os
from helper import generate, extract_text_from_pdf
from pathlib import Path

# Must be the first Streamlit command
st.set_page_config(layout="wide", page_title="Resume Parser App", page_icon="📄")

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
    return sections

def user_interface():
    # Custom CSS
    st.markdown("""
        <style>
        .stApp {
            background-color: #f8f9fa;
        }
        .css-1d391kg {
            padding: 2rem 1rem;
        }
        .stButton>button {
            width: 100%;
            border-radius: 4px;
            height: 45px;
        }
        .upload-block {
            border: 2px dashed #ccc;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            background: white;
        }
        .results-block {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Header with gradient
    st.markdown("""
        <div style='background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0;'>Resume Parser App</h1>
            <p style='color: #e0e0e0; margin: 10px 0 0 0;'>Upload your resume for instant analysis and insights</p>
        </div>
    """, unsafe_allow_html=True)

    # Main content in columns
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("<div class='upload-block'>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("📄 Choose a PDF file", type="pdf")
        if uploaded_file:
            st.success(f"File uploaded: {uploaded_file.name}")
        st.markdown("</div>", unsafe_allow_html=True)

        if uploaded_file:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 Analyze Resume", use_container_width=True):
                with st.spinner("🔄 Processing your resume..."):
                    with open("temp_resume.pdf", "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    text = extract_text_from_pdf("temp_resume.pdf")
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

                    Make sure that the sections are named as "Experience Summary:", "Key Skills:" and "improvements"
                    '''
                    
                    result = generate(prompt + text)

                    print(result)
                    
                    with col2:
                        st.markdown("<div class='results-block'>", unsafe_allow_html=True)
                        st.markdown("### 📊 Analysis Results")
                        
                        # Extract and display score if present
                        if "score" in result.lower():
                            score_line = [line for line in result.split('\n') if 'score' in line.lower()][0]
                            score = int(''.join(filter(str.isdigit, score_line)))
                            st.progress(score/100)
                            st.markdown(f"### Resume Score: {score}/100")
                        
                        # Display the rest of the analysis
                        tabs = st.tabs(["📈 Experience", "🛠️ Skills", "💡 Improvements"])
                        
                        with tabs[0]:
                            st.markdown("#### Professional Experience")
                            experience_section = result.split("Experience Summary:")[1].split("Key Skills:")[0]
                            st.write(experience_section)
                            
                        with tabs[1]:
                            st.markdown("#### Key Skills")
                            skills_section = result.split("Key Skills:")[1].split("Score:")[0]
                            st.write(skills_section)
                            
                        with tabs[2]:
                            st.markdown("#### Suggestions for Improvement")
                            if "score" in result.lower():
                                suggestions = '# Score'+result.split("Score")[1]
                                st.write(suggestions)
                        
                        st.markdown("</div>", unsafe_allow_html=True)

def admin_interface():
    # Header with gradient
    st.markdown("""
        <div style='background: linear-gradient(90deg, #2c3e50 0%, #3498db 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0;'>Resume Parser - Admin Dashboard</h1>
            <p style='color: #e0e0e0; margin: 10px 0 0 0;'>Batch process and manage resumes</p>
        </div>
    """, unsafe_allow_html=True)

    # Admin controls
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("<div class='upload-block'>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader("📄 Upload Multiple Resumes", type="pdf", accept_multiple_files=True)
        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)} files selected")
        st.markdown("</div>", unsafe_allow_html=True)

        if uploaded_files:
            if st.button("🔄 Process All Resumes", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name}...")
                    temp_path = f"temp_resume_{i}.pdf"
                    
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    text = extract_text_from_pdf(temp_path)
                    prompt = '''Always start answering by saying hello there...'''  # Same prompt as before
                    result = generate(prompt + text)
                    
                    parsed_result = parse_analysis_result(result)
                    save_to_db(uploaded_file.name, parsed_result)
                    
                    progress_bar.progress((i + 1)/len(uploaded_files))
                    os.remove(temp_path)
                
                status_text.success("✅ All resumes processed!")

    with col2:
        if st.button("📊 View Database Records", use_container_width=True):
            conn = sqlite3.connect('resumes.db')
            c = conn.cursor()
            c.execute('SELECT filename, experience, skills, contact_details, upload_date FROM resumes')
            rows = c.fetchall()
            conn.close()
            
            if rows:
                st.markdown("<div class='results-block'>", unsafe_allow_html=True)
                st.markdown("### 📁 Stored Resumes")
                
                for row in rows:
                    with st.expander(f"📄 {row[0]} | Uploaded: {row[4]}"):
                        tabs = st.tabs(["Experience", "Skills", "Contact"])
                        
                        with tabs[0]:
                            st.markdown("#### Professional Experience")
                            st.write(row[1])
                            
                        with tabs[1]:
                            st.markdown("#### Skills")
                            st.write(row[2])
                            
                        with tabs[2]:
                            st.markdown("#### Contact Details")
                            st.write(row[3])
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No resumes found in the database")

def main():
    init_db()
    
    # Sidebar navigation with custom styling
    st.sidebar.markdown("""
        <div style='padding: 1rem; background: white; border-radius: 8px;'>
            <h2 style='margin: 0 0 1rem 0;'>Navigation</h2>
        </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.radio("Select Interface", ["👤 User Interface", "🔐 Admin Interface"])
    
    if page == "👤 User Interface":
        user_interface()
    else:
        admin_interface()

if __name__ == "__main__":
    main()