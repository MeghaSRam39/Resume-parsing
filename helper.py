from groq import Groq
import PyPDF2
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import json
import PyPDF2
from pathlib import Path
import docx

def generate(prompt,text):
    load_dotenv(override=True)
    api = os.getenv('groq_api')
    client = Groq(api_key=api)
    
    # print(prompt)
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"{prompt}"
            },
            {
                "role": "user",
                "content": f'{text}',
            }
        ],
        model="llama3-8b-8192",
        temperature=0,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )
    
    response = chat_completion.choices[0].message.content
    print(response)
    # Extract JSON using regex
    import re
    json_pattern = r'\{[\s\S]*\}'
    json_match = re.search(json_pattern, response)

    print(json_match)
    
    try:
        if json_match:
            json_str = json_match.group(0)
            json_response = json.loads(json_str)
            return json_response
        else:
            raise json.JSONDecodeError("No JSON found in response", response, 0)
    except json.JSONDecodeError:
        return {
            "experience": "Error parsing response",
            "skills": "Error parsing response",
            "contact_details": "Error parsing response",
            "score": 0
        }


def extract_text_from_pdf(doc_path):
    try:
        file_path = Path(doc_path)
        if not file_path.exists():
            raise FileNotFoundError(f"The file {doc_path} does not exist")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            with open(doc_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                text = ""
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
                    
                    if page_num < num_pages - 1:
                        text += "\n\n--- Page {} ---\n\n".format(page_num + 1)
            
            return text
            
        elif file_extension == '.docx':
            doc = docx.Document(doc_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
            
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Only .pdf and .docx are supported.")
            
    except Exception as e:
        raise Exception(f"An error occurred while reading the document: {str(e)}")