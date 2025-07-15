import os
import tempfile
from git import Repo

VALID_EXTENSIONS = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.ipynb', '.pbix', '.md', '.html', '.sql', '.css', '.json', '.yaml', '.yml', '.txt', '.DockerFile', '.in', '.toml', '.png', '.hcl', '.csv', '.crt', '.mdx', '.icloud', '.jpeg', '.gif', '.svg', '.sh', '.pdf', '.doc', '.docx', '.xlxs']

def clone_repo(repo_url):
    temp_dir = tempfile.mkdtemp()
    Repo.clone_from(repo_url, temp_dir)
    return temp_dir

def read_code_files(repo_path):
    code_files = {}
    for root, _, files in os.walk(repo_path):
        for file in files:
            if any(file.endswith(ext) for ext in VALID_EXTENSIONS):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code_files[file_path] = f.read()
                except Exception:
                    pass
    return code_files
