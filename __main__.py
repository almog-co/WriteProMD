#!/usr/bin/env python3

from MarkdownToPDFParser import MarkdownToPDF
from PDF import PDF
import sys
import os
import time
import argparse

#####################
# Helper functions
#####################

def file_changed_since(time, filename):
    return os.stat(filename).st_mtime > time

def watch_file(filename):
    currTime = os.stat(filename).st_mtime
    while (not file_changed_since(currTime, filename)):
        time.sleep(0.1)

#####################
# Main
#####################

# Parse the arguments
parser = argparse.ArgumentParser(description='Compile a markdown-like file to a PDF.')
parser.add_argument('filename', metavar='filename', type=str, nargs=1, help='the markdown file to compile')
parser.add_argument('-w', '--watch', action='store_true', help='watch the file for changes')

args = parser.parse_args()

WATCH = args.watch
FILENAME = args.filename[0]

# Check if the file exists
if (not os.path.exists(FILENAME)):
    print("File does not exist: " + FILENAME)
    sys.exit(1)

# Watch the file
try:
    while(True):
        # Open the markdown file
        markdown = open(FILENAME, 'r')

        if (markdown == None):
            print("Could not open file: " + FILENAME)
            sys.exit(1)

        # Read the markdown file
        markdown = markdown.read()

        # Search for @header commands
        headers = []
        layout = None
        lines_to_remove = []
        for i, line in enumerate(markdown.splitlines()):
            if line.startswith('@header'):
                headers = line[8:].strip().split(',')
                lines_to_remove.append(i)
            elif line.startswith('@pagelayout'):
                try: 
                    layout = line.split(' ')[1].strip()
                    lines_to_remove.append(i)
                    if (layout not in ['Legal', 'Letter', 'A4', 'A3', 'A5', 'A6', 'B5', 'Executive', 'Folio', 'Ledger', 'Tabloid']):
                        print('Invalid layout')
                        layout = None
                except:
                    print('Invalid layout')
        
        # Remove the lines
        lines = markdown.splitlines()
        for i, line in enumerate(lines_to_remove):
            lines.pop(line - i)
        markdown = '\n'.join(lines)

        # Set up the PDF
        pdf = PDF(headers, footers=['test'], layout=layout)
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)

        # Parse the markdown file
        parser = MarkdownToPDF(markdown, pdf)

        # Save the PDF
        pdf.output(FILENAME.replace('.md', '.pdf'))

        # Exit if we don't want to watch the file
        if (not WATCH):
            break
        watch_file(FILENAME)
except KeyboardInterrupt:
    pass