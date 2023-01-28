from MarkdownToPDFParser import MarkdownToPDF
from PDF import PDF

# Set up the PDF
pdf = PDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)

# Open the markdown file
markdown = open('test.md', 'r').read()

# Parse the markdown file
parser = MarkdownToPDF(markdown, pdf)

# Save the PDF
pdf.output("test.pdf")