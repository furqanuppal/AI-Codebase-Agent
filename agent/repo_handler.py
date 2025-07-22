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
    cleaned_input = clean_text(user_input)
    matches = {}

    for path, content in code_files.items():
        filename = os.path.basename(path)
        cleaned_filename = clean_text(filename)

        if cleaned_input in cleaned_filename:
            matches[path] = content

    # If nothing found, try fuzzy matching using filename only
    if not matches:
        all_filenames = [os.path.basename(p) for p in code_files]
        closest = get_close_matches(user_input.lower(), all_filenames, n=3, cutoff=0.4)
        for path in code_files:
            if os.path.basename(path) in closest:
                matches[path] = code_files[path]

    return matches
