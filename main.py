from helper import generate, extract_text_from_pdf

pdf_path = 'Uploaded_resumes\data-scientist-1559725114.pdf'
prompt = '''
You will be given the text extracted form a resume. You have to properly extract the relevant information in the following format.

- Experience
- Skills
- Contact details


'''
text = extract_text_from_pdf(pdf_path)

out = generate(prompt + text)
print(out)


