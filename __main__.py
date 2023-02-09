#!/usr/bin/env python3

from MarkdownToPDFParser import MarkdownToPDF
from PDF import PDF
import sys
import os
import time

def file_changed_since(time, filename):
    return os.stat(filename).st_mtime > time

def watch_file(filename):
    currTime = os.stat(filename).st_mtime
    while (not file_changed_since(currTime, filename)):
        time.sleep(0.1)
       
if (len(sys.argv) < 2):
    print("Usage: python main.py <markdown file> [-w]")
    sys.exit(1)

WATCH = False
filename = None

if (len(sys.argv) == 2):
    filename = sys.argv[1]
else:
    for (i, arg) in enumerate(sys.argv):
        if (i == 0):
            continue
        if (arg == '-w'):
            WATCH = True
        else:
            filename = arg
once = True
while (WATCH or once):
    once = False

    # Open the markdown file
    markdown = open(filename, 'r')

    if (markdown == None):
        print("Could not open file: " + filename)
        sys.exit(1)

    # Read the markdown file
    markdown = markdown.read()

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
    pdf.output(filename.replace('.md', '.pdf'))

    # Wait for the file to change
    if (WATCH):
        watch_file(filename)
