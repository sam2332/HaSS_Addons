import re

def extract_moods(line):
    # Define a broader set of regex patterns to capture mood expressions
    patterns = [
        r'\bIt makes me feel so ([\w\s]+)[.!?]',
        r'\bI feel so ([\w\s]+)[.!?]',
        r'\bMakes me feel ([\w\s]+)[.!?]',
        r'\bI\'m feeling so ([\w\s]+)[.!?]',
        r'\bI am feeling so ([\w\s]+)[.!?]',
        r'\bIt makes me feel ([\w\s]+)[.!?]',
        r'\bI\'m feeling ([\w\s]+)[.!?]',
        r'\bI feel ([\w\s]+)[.!?]',
        r'\bIt makes me ([\w\s]+)[.!?]',
        r'\bI\'ve been feeling ([\w\s]+)[.!?]',
        r'\bI am ([\w\s]+)[.!?]',
        r'\bI\'m ([\w\s]+)[.!?]',
        r'\bFeeling ([\w\s]+)[.!?]',
        r'\bThis leaves me ([\w\s]+)[.!?]',
        r'\bLeft me feeling ([\w\s]+)[.!?]',
        r'\bI am left feeling ([\w\s]+)[.!?]',
        r'\bMy mood is ([\w\s]+)[.!?]',
        r'\bThis makes me ([\w\s]+)[.!?]',
        r'\bI can\'t help but feel ([\w\s]+)[.!?]',
        r'\bI was feeling ([\w\s]+)[.!?]',
    ]
    
    # Iterate over each pattern
    for pattern in patterns:
        # Find all matches for the current pattern
        match = re.findall(pattern, line)
        # Return the first match found, stripped of any extra spaces
        if match:
            return match[0].strip()
    
    # Return None if no match is found
    return None