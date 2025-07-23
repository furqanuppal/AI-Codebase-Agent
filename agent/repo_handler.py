import os
import tempfile
import re
from git import Repo
from difflib import get_close_matches

def clone_repo(repo_url):
    temp_dir = tempfile.mkdtemp()
    Repo.clone_from(repo_url, temp_dir)
    return temp_dir

def read_code_files(repo_path):
    code_files = {}
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    code_files[file_path] = content
            except Exception:
                continue
    return code_files

def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def filter_files_by_path(code_files, user_input):
    from difflib import get_close_matches

    def clean(text):
        return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

    cleaned_input = clean(user_input)

    matches = {}

    for path, content in code_files.items():
        relative = os.path.relpath(path)
        cleaned_path = clean(relative)
        if cleaned_input in cleaned_path:
            matches[path] = content

    if matches:
        return matches

    # If no matches found, try fuzzy path match
    rel_paths = [os.path.relpath(p) for p in code_files]
    closest_paths = get_close_matches(user_input.lower(), rel_paths, n=3, cutoff=0.3)
    for path in code_files:
        if os.path.relpath(path) in closest_paths:
            matches[path] = code_files[path]

    return matches

def extract_folder_path_from_input(base_path, user_input):
    """
    Try to infer folder path from user input like:
    "Go into mindsdb folder and then integrations folder"
    """
    # Step 1: Extract candidate folder names using regex or keywords
    # Example regex-based quick extract
    folders = re.findall(r"(?<=into\s|go to\s|inside\s|under\s)(\w+)", user_input.lower())

    # Step 2: Traverse the repo and try to resolve real folder path
    current_path = base_path
    for folder in folders:
        matches = []
        for root, dirs, _ in os.walk(current_path):
            for d in dirs:
                if d.lower() == folder:
                    matches.append(os.path.join(root, d))
        if matches:
            current_path = matches[0]  # choose the first match
        else:
            break  # stop if folder not found

    if current_path == base_path:
        return None  # no folder resolved
    return current_path
