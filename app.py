import streamlit as st
import mysql.connector
import os
import json
from helper import extract_text_from_pdf, generate
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Set page config
st.set_page_config(layout="wide", page_title="Resume Parser & Job Recommendation App", page_icon="📄")

# Database functions
def init_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="meghasram52@"
        )
        c = conn.cursor()
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Database initialization error: {e}")

def save_to_db(name, analysis_result):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="meghasram52@",
            database="stored_resume"
        )
        c = conn.cursor()
        
        # Convert the score to an integer if it's a string
        score = analysis_result.get('score', 0)
        if isinstance(score, str):
            try:
                score = int(score)
            except ValueError:
                score = 0
        
        c.execute("""
            INSERT INTO resumes (file_name, candidate_name, experience, experience_level, skills, education, contact_details, score, upload_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name,
            analysis_result.get('candidate_name', ''),
            analysis_result.get('experience', ''),
            analysis_result.get('experience_level', ''),
            analysis_result.get('skills', ''),
            analysis_result.get('education', ''),
            analysis_result.get('contact_details', ''),
            score,
            datetime.now()
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database save error: {e}")
        return False

# Text extraction
def extract_text_from_docx(filepath):
    try:
        import docx
        doc = docx.Document(filepath)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text(file_path):
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")

# Processing functions
def analyze_resume_with_llama(resume_text, identity):
    try:
        if identity == 'user':
            response = generate(resume_text)
        
        if identity == 'admin': 
            response = generate(resume_text)
            response_dict = json.loads(response)
            return parse_analysis_result_admin(response_dict)
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse response: {e}")  
        return None
    except Exception as e:
        st.error(f"Analysis error: {e}")
        return None


def parse_analysis_result_user(text):
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
 
def parse_analysis_result_admin(response_dict):
    try:
        # Ensure score is an integer
        score = response_dict.get('score', 0)
        if isinstance(score, str):
            try:
                score = int(score)
            except ValueError:
                score = 0
                
        sections = {
            'experience': response_dict.get('experience', 'Not found'),
            'skills': ', '.join(response_dict.get('skills', [])),
            'contact_details': response_dict.get('contact_info', {}),
            'score': score
        }
        
        if isinstance(sections['contact_details'], dict):
            sections['contact_details'] = '\n'.join(
                [f"{k}: {v}" for k, v in sections['contact_details'].items()]
            )
        return sections
    except Exception as e:
        st.error(f"Parsing error: {e}")
        return None

def process_resume(uploaded_file, identity):
    try:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        resume_text = extract_text(uploaded_file.name)
        if identity == 'user':
            prompt = f"""Analyze the following resume/CV and provide results in JSON format with these fields:
    - experience: A string summarizing professional experience
    - skills: A string listing key skills
    - improvements: A deep analysis(tell the positive and negative parts of the resume) into the resume and ways to improve the quality of resume. There should be 3 positives and negatives. The suggstions should have atleast 5 ways to improve the resume. It should be in this format:
        - positive
        - negative
        - suggestions
    - contact_details: A string with contact information
    - score: A number from 0-100 rating the resume's overall quality
    - job_recommendations: A string with recommended job position for each candidate"""

            analysis_result = generate(prompt,resume_text)

        elif identity == 'admin':
            prompt = f"""Analyze the following resume/CV and provide results in JSON format with these fields:
    - candidate_name: The name of the candidate
    - experience: A string summarizing professional experience
    - skills: A string listing key skills
    - contact_details: A string with contact information
    - score: A number from 0-100 rating the resume's overall quality
    - experince level: It should be ['Entry', 'Mid-Level', 'Senior', 'Expert'], based on years of experience (or if mentioned in resume) [3+ years for mid, 5+ for senior and 10+ expert]
    - education: Should contain the degrees that the candidate hold, separated by comma(Eg: BTech, MTech)"""
            analysis_result = generate(prompt, resume_text)
            
        else:
            raise Exception('Invalid identity')
        
        os.remove(uploaded_file.name)
        return analysis_result
    except Exception as e:
        st.error(f"Processing error: {e}")
        return None

def check_resume_exists(filename):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="meghasram52@",
            database="stored_resume"
        )
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM resumes WHERE file_name = %s", (filename,))
        count = c.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        st.error(f"Database check error: {e}")
        # Return False in case of error to allow upload attempt
        return False

def user_interface():
    # Custom CSS for better styling
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Poppins:wght@400;700&family=Montserrat:wght@400;700&display=swap');

        /* Gradient background for the header - Silver touch */
        .header {
            background: linear-gradient(135deg, #4b6cb7, #9baec8); /* Blue to silver-like gradient */
            padding: 2rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
            font-family: 'Poppins', sans-serif;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        /* Card styling */
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            font-family: 'Roboto', sans-serif;
        }
        
        /* Button styling - Light green gradient */
        .stButton>button {
            background: linear-gradient(135deg, #a8e6cf, #dcedc1); /* Light green gradient */
            color: #333; /* Dark text for contrast */
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Roboto', sans-serif;
        }
        
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            padding: 1rem;
            margin-top: 2rem;
            color: white;
            background-color: #2e8b57; /* Medium green color */
            font-size: 0.9rem;
            font-family: 'Montserrat', sans-serif;
            border-radius: 8px;
        }
        
        /* Improve spacing */
        .stMarkdown {
            margin-bottom: 1.5rem;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            margin-bottom: 1.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            transition: all 0.3s ease;
            font-family: 'Roboto', sans-serif;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(168, 230, 207, 0.1); /* Light green with transparency */
        }
        
        .stTabs [aria-selected="true"] {
            background: #a8e6cf; /* Light green */
            color: #333; /* Dark text for contrast */
        }

        /* Custom font for headlines */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Montserrat', sans-serif;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header with gradient
    st.markdown("""
        <div class="header">
            <h1 style="margin: 0;">📄 Resume Parser App</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.1rem;">Upload your resume for instant analysis and insights</p>
        </div>
    """, unsafe_allow_html=True)

    # Main content in columns
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("📄 Choose a file", type=["pdf", "docx"])
        if uploaded_file:
            st.success(f"File uploaded: {uploaded_file.name}")
        st.markdown("</div>", unsafe_allow_html=True)

        if uploaded_file:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 Analyze Resume", use_container_width=True):
                with st.spinner("🔄 Processing your resume..."):
                    analysis_result = process_resume(uploaded_file, identity='user')

                    with col2:
                        st.markdown("<div class='card'>", unsafe_allow_html=True)
                        st.markdown("### 📊 Analysis Results")
                        
                        score = analysis_result.get('score', 0)
                        if isinstance(score, str):
                            try:
                                score = int(score)
                            except ValueError:
                                score = 0
                                
                        st.progress(score/100)
                        st.markdown(f"### Resume Score: {score}/100")
                        
                        # Display the rest of the analysis
                        tabs = st.tabs(["📈 Experience", "🛠 Skills", "💡 Improvements", "💼 Job Recommendations", "🌐 3D Insights"])
                        
                        with tabs[0]:
                            st.markdown("#### Professional Experience")
                            st.write(analysis_result.get('experience', 'No experience found'))
                            
                        with tabs[1]:
                            st.markdown("<div class='card'>", unsafe_allow_html=True)
                            st.markdown("#### Key Skills")
                            st.write(analysis_result.get('skills', 'No skills found'))
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                        with tabs[2]:
                            st.markdown("#### Comprehensive Feedback")
                            improvements = analysis_result.get('improvements', {})
                            
                            if isinstance(improvements, dict):
                                # Positive Aspects
                                st.markdown("<div class='card' style='background: #e8f5e9; border-left: 4px solid #2ecc71;'>", unsafe_allow_html=True)
                                st.markdown("##### ✅ Strengths")
                                positives = improvements.get('positive', [])
                                if positives:
                                    if isinstance(positives, list):
                                        for strength in positives:
                                            st.markdown(f"- {strength}")
                                    else:
                                        st.write(positives)
                                else:
                                    st.info("No positive aspects identified")
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                                # Negative Aspects
                                st.markdown("<div class='card' style='background: #ffebee; border-left: 4px solid #e74c3c;'>", unsafe_allow_html=True)
                                st.markdown("##### ❌ Areas for Improvement")
                                negatives = improvements.get('negative', [])
                                if negatives:
                                    if isinstance(negatives, list):
                                        for weakness in negatives:
                                            st.markdown(f"- {weakness}")
                                    else:
                                        st.write(negatives)
                                else:
                                    st.info("No negative aspects identified")
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                                # Suggestions
                                st.markdown("<div class='card' style='background: #e3f2fd; border-left: 4px solid #3498db;'>", unsafe_allow_html=True)
                                st.markdown("##### 📈 Actionable Recommendations")
                                suggestions = improvements.get('suggestions', [])
                                if suggestions:
                                    if isinstance(suggestions, list):
                                        for suggestion in suggestions:
                                            st.markdown(f"- {suggestion}")
                                    else:
                                        st.write(suggestions)
                                else:
                                    st.info("No specific suggestions available")
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                            else:
                                st.markdown("##### General Feedback")
                                st.write(improvements)

                            # Final tip
                            st.markdown("---")
                            st.markdown("💡 Implement these suggestions to enhance your resume's impact")
                        
                        st.markdown("</div>", unsafe_allow_html=True)

                        with tabs[3]:
                            st.markdown("#### 💼 Job Recommendations")
                            st.write(analysis_result.get('job_recommendations', 'No jobs recommended'))

                        with tabs[4]:
                            st.markdown("#### 🌐 3D Insights")
                            # Add a 3D scatter plot using Plotly
                            st.markdown("##### Skills Distribution in 3D")
                            skills = analysis_result.get('skills', '').split(', ')
                            if skills:
                                # Generate random data for 3D visualization
                                import numpy as np
                                np.random.seed(42)
                                x = np.random.rand(len(skills))
                                y = np.random.rand(len(skills))
                                z = np.random.rand(len(skills))

                                # Create a 3D scatter plot
                                fig = go.Figure(data=[go.Scatter3d(
                                    x=x,
                                    y=y,
                                    z=z,
                                    mode='markers+text',
                                    text=skills,
                                    marker=dict(
                                        size=10,
                                        color=z,
                                        colorscale='Viridis',
                                        opacity=0.8
                                    ),
                                    textposition="top center"
                                )])

                                # Update layout for better visualization
                                fig.update_layout(
                                    scene=dict(
                                        xaxis_title='Skill Relevance',
                                        yaxis_title='Skill Demand',
                                        zaxis_title='Skill Experience'
                                    ),
                                    margin=dict(l=0, r=0, b=0, t=0),
                                    height=600,  # Increased height for better visibility
                                    scene_camera=dict(
                                        eye=dict(x=1.5, y=1.5, z=0.5)  # Adjust camera angle for better view
                                    )
                                )

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("No skills found for 3D visualization.")

    # Footer
    st.markdown("""
        <div class="footer">
            <p>Made by Resume Parser Team ✨</p>
        </div>
    """, unsafe_allow_html=True)

def admin_interface():
    # Custom CSS for better styling
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Poppins:wght@400;700&family=Montserrat:wght@400;700&display=swap');

        /* Gradient background for the header - Silver touch */
        .header {
            background: linear-gradient(135deg, #4b6cb7, #9baec8); /* Blue to silver-like gradient */
            padding: 2rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
            font-family: 'Poppins', sans-serif;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        /* Card styling */
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            font-family: 'Roboto', sans-serif;
        }
        
        /* Button styling - Light green gradient */
        .stButton>button {
            background: linear-gradient(135deg, #a8e6cf, #dcedc1); /* Light green gradient */
            color: #333; /* Dark text for contrast */
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Roboto', sans-serif;
        }
        
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Footer styling */
        .footer {
        text-align: center;
            padding: 1rem;
            margin-top: 2rem;
            color: white;
            background-color: #2e8b57; /* Medium green color */
            font-size: 0.9rem;
            font-family: 'Montserrat', sans-serif;
            border-radius: 8px;
        }
        
        /* Improve spacing */
        .stMarkdown {
            margin-bottom: 1.5rem;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            margin-bottom: 1.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            transition: all 0.3s ease;
            font-family: 'Roboto', sans-serif;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(168, 230, 207, 0.1); /* Light green with transparency */
        }
        
        .stTabs [aria-selected="true"] {
            background: #a8e6cf; /* Light green */
            color: #333; /* Dark text for contrast */
        }

        /* Custom font for headlines */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Montserrat', sans-serif;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header with gradient
    st.markdown("""
        <div class="header">
            <h1 style="margin: 0;">📄 Resume Parser - Recruiter Dashboard</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.1rem;">Advanced Resume Screening and Candidate Management</p>
        </div>
    """, unsafe_allow_html=True)

    # Admin Upload
    with st.expander("📤 Bulk Upload Resumes (Admin Only)", expanded=True):
        uploaded_files = st.file_uploader(
            "Upload multiple resumes (PDF/DOCX)", 
            type=["pdf", "docx"], 
            accept_multiple_files=True,
            key="admin_upload"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    try:
                        # Check if resume already exists in database
                        if check_resume_exists(uploaded_file.name):
                            st.warning(f"Resume {uploaded_file.name} already exists in database. Skipping.")
                            continue
                            
                        analysis_result = process_resume(uploaded_file, identity='admin')
                        
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
                ["Artificial Intelligence", "AWS", "Azure", "C++", "C#", "C", "Cloud Computing", "CSS", "Data Analysis",
                 "Data Science", "Digital Marketing", "Java", "Machine Learning", "Project Management", "Python", "React", "SQL" ])
        
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
            SELECT candidate_name, experience, skills, contact_details, score, upload_date, education, experience_level
            FROM resumes 
            WHERE score >= %s
        '''
        params = [min_score]

        if search_skills:
            skill_conditions = ' OR '.join(['skills LIKE %s' for _ in search_skills])
            query += f' AND ({skill_conditions})'
            params.extend([f'%{skill}%' for skill in search_skills])

        if experience_level != "Any":
            query += f' AND experience_level LIKE %s'
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
                    df = pd.DataFrame(rows, columns=["Candidate Name", "Experience", "Skills", "Contact", "Score", "Upload Date", "Education", "Experience Level"])
                    df = df[df["Candidate Name"].isin(selected_candidates)]
                    
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
                # Ensure score is an integer for comparison
                if isinstance(score, str):
                    try:
                        score = int(score)
                    except ValueError:
                        score = 0
                        
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
                            exp_level = row[7]
                            st.metric("Experience Level", exp_level)

        else:
            st.info("No resumes found in the database")

        conn.close()
    except Exception as e:
        st.error(f"Database connection error: {e}")

    # Footer
    st.markdown("""
        <div class="footer">
            <p>Made by Resume Parser Team ✨</p>
        </div>
    """, unsafe_allow_html=True)

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