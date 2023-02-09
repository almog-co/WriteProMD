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
        pdf.output(FILENAME.replace('.md', '.pdf'))

        # Exit if we don't want to watch the file
        if (not WATCH):
            break
        watch_file(FILENAME)
except KeyboardInterrupt:
    pass