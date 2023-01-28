from MarkdownToPDFParser import MarkdownToPDF
from PDF import PDF

# Open the markdown file
markdown = open('test.md', 'r').read()

# Search for @header commands
headers = []
for line in markdown.splitlines():
    if line.startswith('@header'):
        headers = line[8:].strip().split(',')
        break
    
# Set up the PDF
pdf = PDF(headers, footers=['test'])
pdf.add_page()
pdf.set_font("Helvetica", size=12)

# Parse the markdown file
parser = MarkdownToPDF(markdown, pdf)

# Save the PDF
pdf.output("test.pdf")