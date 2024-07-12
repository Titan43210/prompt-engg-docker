from PyPDF2 import PdfReader

def process_pdf(file_path):
    # Create a PDF reader object
    reader = PdfReader(file_path)

    # Print the number of pages in the PDF file
    num_pages = len(reader.pages)
    print(f'Number of pages in the PDF: {num_pages}')

    # Initialize an empty list to store the text from all pages
    all_text = []

    # Iterate over all pages and extract text
    for page_num in range(num_pages):
        page = reader.pages[page_num]
        text = page.extract_text()
        all_text.append(text)

    # Join all the extracted text into a single string
    full_text = "\n".join(all_text)
    return full_text



