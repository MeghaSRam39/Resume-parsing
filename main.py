from helper import generate, extract_text_from_pdf

pdf_path = 'Uploaded_resumes\data-scientist-1559725114.pdf'
prompt = '''
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

'''
text = extract_text_from_pdf(pdf_path)

out = generate(prompt + text)
print(out)


