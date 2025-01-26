import streamlit as st
import mysql.connector
import os
import json
from helper import  extract_text_from_pdf
import pandas as pd
from datetime import datetime


def generate(resume_text):
    """Sample generator function returning fixed response with score"""
    return json.dumps({
        "experience": "Does some ML.",
        "skills": ["Machine Learning", "JavaScript", "React", "Node.js", "SQL", "AWS"],
        "contact_info": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1 (555) 123-4567",
            "linkedin": "linkedin.com/in/johndoe"
        },
        "score": 25
    })


# Set page config
st.set_page_config(layout="wide", page_title="Resume Parser App", page_icon="📄")

# Database functions
def init_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="meghasram52@"
        )
        c = conn.cursor()
        c.execute("CREATE DATABASE IF NOT EXISTS stored_resume")
        c.execute("USE stored_resume")
        c.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                experience TEXT,
                skills TEXT,
                contact_details TEXT,
                score INT,
                upload_date DATETIME
            )
        """)
        # Check and add score column if missing
        c.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'stored_resume' 
            AND TABLE_NAME = 'resumes'
            AND COLUMN_NAME = 'score'
        """)
        if c.fetchone()[0] == 0:
            c.execute("ALTER TABLE resumes ADD COLUMN score INT AFTER contact_details")
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Database initialization error: {e}")

def save_to_db(filename, analysis_result):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="meghasram52@",
            database="stored_resume"
        )
        c = conn.cursor()
        c.execute("""
            INSERT INTO resumes (filename, experience, skills, contact_details, score, upload_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            filename,
            analysis_result.get('experience', ''),
            analysis_result.get('skills', ''),
            analysis_result.get('contact_details', ''),
            analysis_result.get('score', 0),
            datetime.now()
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database save error: {e}")
        return False

# Processing functions
def analyze_resume_with_llama(resume_text):
    try:
        response = generate(resume_text)
        response_dict = json.loads(response)
        return parse_analysis_result(response_dict)
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse response: {e}")
        return None
    except Exception as e:
        st.error(f"Analysis error: {e}")
        return None

def parse_analysis_result(response_dict):
    try:
        sections = {
            'experience': response_dict.get('experience', 'Not found'),
            'skills': ', '.join(response_dict.get('skills', [])),
            'contact_details': response_dict.get('contact_info', {}),
            'score': int(response_dict.get('score', 0))
        }
        
        if isinstance(sections['contact_details'], dict):
            sections['contact_details'] = '\n'.join(
                [f"{k}: {v}" for k, v in sections['contact_details'].items()]
            )
        return sections
    except Exception as e:
        st.error(f"Parsing error: {e}")
        return None

def process_resume(uploaded_file):
    try:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        resume_text = extract_text_from_pdf(uploaded_file.name)
        analysis_result = analyze_resume_with_llama(resume_text)
        
        os.remove(uploaded_file.name)
        return analysis_result
    except Exception as e:
        st.error(f"Processing error: {e}")
        return None

# Interfaces
def user_interface():
    st.markdown("""
        <div style='background: linear-gradient(90deg, #2c3e50 0%, #3498db 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0;'>Resume Parser - Candidate Portal</h1>
            <p style='color: #e0e0e0; margin: 10px 0 0 0;'>Upload your resume for automated analysis</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("### 📤 Upload Your Resume")
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], key="user_upload")
        
        if uploaded_file:
            with st.spinner("Analyzing your resume..."):
                analysis_result = process_resume(uploaded_file)
                if analysis_result:
                    if save_to_db(uploaded_file.name, analysis_result):
                        st.success("Resume processed and stored successfully!")
                    else:
                        st.error("Failed to store resume in database")

    with col2:
        if uploaded_file and analysis_result:
            st.markdown("### 📄 Analysis Results")
            with st.expander("View Details"):
                st.markdown("#### Professional Experience")
                st.write(analysis_result.get('experience', 'No experience found'))
                
                st.markdown("#### Key Skills")
                st.write(analysis_result.get('skills', 'No skills found'))
                
                st.markdown("#### Contact Details")
                st.write(analysis_result.get('contact_details', 'No contact information found'))
                
                st.markdown("#### Resume Score")
                score = analysis_result.get('score', 0)
                score_color = "#2ecc71" if score >= 75 else "#f1c40f" if score >= 50 else "#e74c3c"
                st.markdown(f"<h3 style='color: {score_color};'>{score}/100</h3>", unsafe_allow_html=True)

def admin_interface():
    st.markdown("""
        <div style='background: linear-gradient(90deg, #2c3e50 0%, #3498db 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0;'>Resume Parser - Recruiter Dashboard</h1>
            <p style='color: #e0e0e0; margin: 10px 0 0 0;'>Advanced Resume Screening and Candidate Management</p>
        </div>
    """, unsafe_allow_html=True)

    # Admin Upload
    with st.expander("📤 Bulk Upload Resumes (Admin Only)", expanded=True):
        uploaded_files = st.file_uploader(
            "Upload multiple resumes (PDF only)", 
            type=["pdf"], 
            accept_multiple_files=True,
            key="admin_upload"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    try:
                        analysis_result = process_resume(uploaded_file)
                        if analysis_result:
                            if save_to_db(uploaded_file.name, analysis_result):
                                st.success(f"Processed and stored: {uploaded_file.name}")
                            else:
                                st.error(f"Failed to store {uploaded_file.name}")
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")

    # Search and Filter
    with st.expander("🔍 Advanced Search"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            search_skills = st.multiselect("Filter by Skills", 
                ["Python", "Machine Learning", "React", "SQL", "Cloud Computing", "Data Analysis"])
        
        with col2:
            experience_level = st.selectbox("Experience Level", 
                ["Any", "Entry", "Mid-Level", "Senior", "Expert"])
        
        with col3:
            min_score = st.slider("Minimum Score", 0, 100, 70)
        
        with col4:
            upload_date_filter = st.date_input("Uploaded After")

    # Database Query
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="meghasram52@",
            database="stored_resume"
        )
        c = conn.cursor()

        query = '''
            SELECT filename, experience, skills, contact_details, score, upload_date 
            FROM resumes 
            WHERE score >= %s
        '''
        params = [min_score]

        if search_skills:
            skill_conditions = ' OR '.join(['skills LIKE %s' for _ in search_skills])
            query += f' AND ({skill_conditions})'
            params.extend([f'%{skill}%' for skill in search_skills])

        if experience_level != "Any":
            query += ' AND experience LIKE %s'
            params.append(f'%{experience_level}%')

        if upload_date_filter:
            query += ' AND upload_date >= %s'
            params.append(upload_date_filter.strftime('%Y-%m-%d'))

        c.execute(query, params)
        rows = c.fetchall()

        # Display Results
        if rows:
            st.markdown("### 📁 Candidate Database")
            
            # Selection and Export
            selected_candidates = st.multiselect(
                "Select Candidates", 
                [row[0] for row in rows]
            )
            
            # Export
            if selected_candidates:
                st.markdown("### 🚀 Bulk Actions")
                export_format = st.selectbox("Export Format", ["CSV", "Excel"])
                
                if st.button("Export Selected Candidates"):
                    df = pd.DataFrame(rows, columns=["Filename", "Experience", "Skills", "Contact", "Score", "Upload Date"])
                    df = df[df["Filename"].isin(selected_candidates)]
                    
                    if export_format == "CSV":
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="candidates.csv",
                            mime="text/csv"
                        )
                    elif export_format == "Excel":
                        excel_file = df.to_excel(index=False)
                        st.download_button(
                            label="Download Excel",
                            data=excel_file,
                            file_name="candidates.xlsx",
                            mime="application/vnd.ms-excel"
                        )

            # Candidate List
            for row in rows:
                score = row[4]
                with st.expander(f"📄 {row[0]} | Score: {score} | Uploaded: {row[5]}"):
                    score_color = "#2ecc71" if score >= 75 else "#f1c40f" if score >= 50 else "#e74c3c"
                    st.markdown(f"<span style='color: {score_color}'>Resume Score: {score}/100</span>", unsafe_allow_html=True)
                    
                    tabs = st.tabs(["Experience", "Skills", "Contact", "Details"])
                    
                    with tabs[0]:
                        st.markdown("#### Professional Experience")
                        st.write(row[1])
                        
                    with tabs[1]:
                        st.markdown("#### Skills")
                        st.write(row[2])
                        
                    with tabs[2]:
                        st.markdown("#### Contact Details")
                        st.write(row[3])
                    
                    with tabs[3]:
                        st.markdown("#### Candidate Metrics")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Resume Score", f"{score}/100")
                        with col2:
                            exp_level = "Senior" if "senior" in row[1].lower() else "Mid-Level" if "mid" in row[1].lower() else "Entry"
                            st.metric("Experience Level", exp_level)

        else:
            st.info("No resumes found in the database")

        conn.close()
    except Exception as e:
        st.error(f"Database connection error: {e}")

# Main app
def main():
    init_db()
    
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