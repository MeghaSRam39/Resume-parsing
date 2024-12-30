import PyPDF2
import sys
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
    
    Returns:
        str: Extracted text from the PDF
    
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If there's an error reading the PDF
    """
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

def save_text_to_file(text, output_path):
    """
    Save extracted text to a file.
    
    Args:
        text (str): Text to save
        output_path (str): Path where to save the text file
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)

def main():
    # Example usage
    pdf_path = r"C:\Users\megha\OneDrive\Desktop\resume-parser\resume\Uploaded_Resumes\resume 3.pdf"  # Replace with your PDF path
    output_path = "output.txt"  # Replace with desired output path
    
    try:
        # Extract text
        extracted_text = extract_text_from_pdf(pdf_path)
        
        # Save to file
        save_text_to_file(extracted_text, output_path)
        
        print(f"Text has been extracted and saved to {output_path}")
        
        # Print first 500 characters as preview
        print("\nPreview of extracted text:")
        print(extracted_text)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()