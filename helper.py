from groq import Groq
import PyPDF2
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import json
# def generate(text):
#     load_dotenv(override=True)
#     api = os.getenv('groq_api')

#     client = Groq(api_key=api)
#     chat_completion = client.chat.completions.create(
#         messages=[
#             {
#                 "role": "system",
#                 "content": "you are a helpful assistant."
#             },
#             {
#                 "role": "user",
#                 "content":f"{text}",
#             }
#         ],

#         model="llama3-8b-8192",
#         temperature=0,
#         max_tokens=1024,
#         top_p=1,
#         stop=None,
#         stream=False,
#     )

#     return chat_completion.choices[0].message.content

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

def extract_text_from_pdf(pdf_path):
    try:
        # Check if file exists
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"The file {pdf_path} does not exist")
        
        # Open the PDF file in binary mode
        with open(pdf_path, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Get the number of pages
            num_pages = len(pdf_reader.pages)
            
            # Initialize text variable
            text = ""
            
            # Extract text from each page
            for page_num in range(num_pages):
                # Get the page object
                page = pdf_reader.pages[page_num]
                
                # Extract text from page
                text += page.extract_text()
                
                # Add a page separator if it's not the last page
                if page_num < num_pages - 1:
                    text += "\n\n--- Page {} ---\n\n".format(page_num + 1)
            
            return text

    except Exception as e:
        raise Exception(f"An error occurred while reading the PDF: {str(e)}")