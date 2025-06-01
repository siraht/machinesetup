import os
import re
import argparse
from datetime import datetime, timedelta

# Function to parse date strings from command line
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")

# Set up command-line argument parser
parser = argparse.ArgumentParser(description='Extract Dreams and My Journal sections from Obsidian daily notes.')
parser.add_argument('--start_date', type=parse_date, default=None, help='Start date in YYYY-MM-DD format')
parser.add_argument('--end_date', type=parse_date, default=None, help='End date in YYYY-MM-DD format')
parser.add_argument('--vault_path', default='/home/travis/Documents/Zettlekasten.md/Daily notes', help='Path to daily notes directory')
parser.add_argument('--output_file', default='journalinganddreams.md', help='Output file name')

# Parse the arguments
args = parser.parse_args()

# Set end_date to today if not provided
if args.end_date is None:
    end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
else:
    end_date = args.end_date

# Set start_date to 30 days before end_date if not provided
if args.start_date is None:
    start_date = end_date - timedelta(days=30)
else:
    start_date = args.start_date

# Validate that start_date is not after end_date
if start_date > end_date:
    print("Error: start_date cannot be after end_date.")
    exit(1)

# Verify that vault_path is a valid directory
if not os.path.isdir(args.vault_path):
    print(f"Error: {args.vault_path} is not a valid directory.")
    exit(1)

# Inform the user of the date range
print(f"Extracting notes from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

# List all .md files in the vault directory
files = [f for f in os.listdir(args.vault_path) if f.endswith('.md')]

# Filter files by date and sort chronologically
dated_files = []
for f in files:
    match = re.match(r'(\d{4}-\d{2}-\d{2})\.md', f)
    if match:
        date_str = match.group(1)
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            if start_date <= date <= end_date:
                dated_files.append((date, f))
        except ValueError:
            pass
dated_files.sort(key=lambda x: x[0])

# Report the number of notes found
print(f"Found {len(dated_files)} notes in the specified date range.")

# Function to parse sections from content
def parse_sections(content):
    sections = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        match = re.match(r'^##\s+(.*)$', lines[i])
        if match:
            heading = match.group(1).strip()
            section_content = []
            i += 1
            while i < len(lines):
                # Stop only at the next main section (## or #)
                if re.match(r'^#{1,2}\s+', lines[i]):
                    break
                section_content.append(lines[i])
                i += 1
            sections.append((heading, '\n'.join(section_content).strip()))
        else:
            i += 1
    return sections

# Extract and collect content
output_lines = []
for date, filename in dated_files:
    file_path = os.path.join(args.vault_path, filename)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        sections = parse_sections(content)
        dreams_content = []
        journal_content = []
        for heading, section_content in sections:
            if heading in ["Dreams", "[[My Dream Journal]]"]:
                dreams_content.append(section_content)
            elif heading == "[[My Journal]]":
                journal_content.append(section_content)
        if dreams_content:
            combined_dreams = '\n'.join(dreams_content)
            output_lines.append(f"## Dreams - {date.strftime('%Y-%m-%d')}\n\n{combined_dreams}\n")
        if journal_content:
            combined_journal = '\n'.join(journal_content)
            output_lines.append(f"## My Journal - {date.strftime('%Y-%m-%d')}\n\n{combined_journal}\n")

# Write the extracted content to the output file
with open(args.output_file, 'w', encoding='utf-8') as outfile:
    outfile.write('\n'.join(output_lines))

print(f"Content extracted and saved to {args.output_file}")