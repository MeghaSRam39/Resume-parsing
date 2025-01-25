import streamlit as st
import mysql.connector
import os
from helper import generate, extract_text_from_pdf
from pathlib import Path
import pandas as pd
import csv

# Must be the first Streamlit command
st.set_page_config(layout="wide", page_title="Resume Parser App", page_icon="📄")

def init_db():
    """Initialize the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host="localhost",          # Replace with your MySQL server address
            user="root",      # Replace with your MySQL username
            password="meghasram52@",  # Replace with your MySQL password
            database="stored_resume"   # Your MySQL database name
        )
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                experience TEXT,
                skills TEXT,
                contact_details TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    except mysql.connector.Error as e:
        st.error(f"Database initialization error: {e}")

# Save Data to Database
def save_to_db(filename, analysis_result):
    """Save the analysis results to the database."""
    conn = mysql.connector.connect(
        host="localhost",  # Update with your DB credentials
        user="root",
        password="your_password",
        database="stored_resume"
    )
    c = conn.cursor()
    c.execute('''
        INSERT INTO resumes (filename, experience, skills, contact_details, score, suggestions)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (
        filename,
        analysis_result['experience'],
        analysis_result['skills'],
        analysis_result['contact_details'],
        analysis_result['score'],
        analysis_result['suggestions']
    ))
    conn.commit()
    conn.close()


def analyze_resume_with_llama(resume_text):
    """Send resume text to Llama 3 model API and get structured output."""
    prompt = f"""
    You are a resume screening assistant. Extract and summarize the following resume's content.

    Provide the output in this structured format:
    Experience Summary: ...
    Key Skills: ...
    Resume Score: ...
    Suggestions: ...
    Input Resume:
    {resume_text}
    """
    # Call Llama 3 API (replace with actual API call)
    response = generate(prompt)
    print(response)
    return parse_analysis_result(response)
    

def parse_analysis_result(response):
    """Parse the Llama 3 API response into structured fields."""
    sections = {'experience': '', 'skills': '', 'contact_details': '', 'score': '', 'suggestions': ''}
    
    if "Experience Summary:" in response:
        sections['experience'] = response.split("Experience Summary:")[1].split("Key Skills:")[0].strip()
    if "Key Skills:" in response:
        sections['skills'] = response.split("Key Skills:")[1].split("Resume Score:")[0].strip()
    if "Resume Score:" in response:
        score_line = response.split("Resume Score:")[1].split("Suggestions:")[0].strip()
        sections['score'] = int(''.join(filter(str.isdigit, score_line)))
    if "Suggestions:" in response:
        sections['suggestions'] = response.split("Suggestions:")[1].strip()
    
    return sections


def process_resume(uploaded_file):
    """Handle uploaded resume, analyze it, and store results."""
    if uploaded_file:
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())

        resume_text = extract_text_from_pdf("temp_resume.pdf")
        analysis_result = analyze_resume_with_llama(resume_text)
        
        # Save results to DB
        save_to_db(uploaded_file.name, analysis_result)
        
        return analysis_result


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
    st.markdown("""
        <div style='background: linear-gradient(90deg, #2c3e50 0%, #3498db 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0;'>Resume Parser - Recruiter Dashboard</h1>
            <p style='color: #e0e0e0; margin: 10px 0 0 0;'>Advanced Resume Screening and Candidate Management</p>
        </div>
    """, unsafe_allow_html=True)

    # Enhanced search and filter options
    with st.expander("🔍 Advanced Search"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_skills = st.multiselect("Filter by Skills", 
                ["Python", "Machine Learning", "React", "SQL", "Cloud Computing", "Data Analysis"])
        
        with col2:
            experience_level = st.selectbox("Experience Level", 
                ["Any", "Entry", "Mid-Level", "Senior", "Expert"])
        
        with col3:
            min_score = st.slider("Minimum Resume Score", 0, 100, 70)

    # Database query with advanced filtering
    conn = mysql.connector.connect(
    host="localhost",          # Replace with your MySQL server's hostname
    user="root",      # Replace with your MySQL username
    password="meghasram52@",  # Replace with your MySQL password
    database="stored_resume"   # The database you created in MySQL
)

    query = '''
        SELECT filename, experience, skills, contact_details, upload_date 
        FROM resumes 
        WHERE 1=1
    '''
    params = []

    if search_skills:
        skill_conditions = ' OR '.join(['skills LIKE ?' for _ in search_skills])
        query += f' AND ({skill_conditions})'
        params.extend([f'%{skill}%' for skill in search_skills])

    if experience_level != "Any":
        query += ' AND experience LIKE ?'
        params.append(f'%{experience_level}%')

    c = conn.cursor()
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    # Candidate Management Section
    
    

    conn = mysql.connector.connect(
    host="localhost",          # Replace with your MySQL server's hostname
    user="root",      # Replace with your MySQL username
    password="meghasram52@",  # Replace with your MySQL password
    database="stored_resume"   # The database you created in MySQL
)

    c = conn.cursor()
    c.execute('SELECT filename, experience, skills, contact_details, upload_date FROM resumes')
    rows = c.fetchall()
    conn.close()
    
    if rows:
        st.markdown("### 📁 Stored Resumes")
        
        # Create a multiselect for candidates
        selected_candidates = st.multiselect(
            "Select Candidates", 
            [row[0] for row in rows]
        )
        
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
        
        # Export section
        if selected_candidates:
            st.markdown("### 🚀 Bulk Actions")
            export_format = st.selectbox("Export Selected Candidates", 
                ["CSV", "PDF", "Excel"])
            
            if st.button("Export Selected Candidates"):
                st.success(f"Exported {len(selected_candidates)} candidates as {export_format}")
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