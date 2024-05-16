import PyPDF2

def extract_data_from_pdf(pdf_file):
    # Open the PDF file
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        # Extract text from each page
        text = ''
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extractText()
    return text

def process_data(text):
    # Process the extracted text to identify categories and counts
    # This might involve parsing the text to find relevant information
    # For simplicity, let's assume the text contains category names and counts in a specific format
    categories = []
    counts = []
    # Process the text to extract categories and counts
    # Example: "Category A: 10, Category B: 20, Category C: 30"
    for segment in text.split(','):
        category, count = segment.strip().split(':')
        categories.append(category)
        counts.append(int(count))
    return categories, counts
