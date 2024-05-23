import re
import json

def remove_ansi_escape_codes(text):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def extract_keywords(data):
    lines = data.split('\n')
    keywords = []
    for line in lines:
        line = re.sub(r'^\d+\.\s*', '', line)  # Remove leading numbers followed by a dot and space
        line = line.strip("\"")  # Remove leading and trailing quotation marks
        if line:
            keywords.append(line)
    return keywords

def parse_serp_results(raw_results):
    cleaned_results = remove_ansi_escape_codes(raw_results)
    return json.loads(cleaned_results)
