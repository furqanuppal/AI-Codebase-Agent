# Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
# .\venv\Scripts\Activate.ps1

import sys
from dotenv import load_dotenv
from agent.repo_handler import clone_repo, read_code_files, filter_files_by_path
from agent.summarizer import summarize_repo, generate_project_summary
from agent.readme_generator import generate_readme
from agent.qa import answer_question

load_dotenv()

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <Github Repo URL>")
        return

    repo_url = sys.argv[1]
    repo_path = clone_repo(repo_url)
    code_files = read_code_files(repo_path)

    print(f"\n📁 Repo cloned. Total readable code/text files: {len(code_files)}")

    # Ask user what to summarize
    print("\nWhat do you want to summarize?")
    summary_scope = input("Enter folder name, file name, or 'all': ").strip().lower()

    if summary_scope == "all":
        files_to_summarize = code_files
    else:
        files_to_summarize = filter_files_by_path(code_files, summary_scope)

    if not files_to_summarize:
        print(f"⚠️ No matching files found for '{summary_scope}'. Exiting.")
        return

    print(f"\n🔍 Found {len(files_to_summarize)} matching files. Starting summarization...")

    file_summaries = summarize_repo(files_to_summarize)

    with open("file_summaries.txt", "w", encoding="utf-8") as f:
        for path, summary in file_summaries.items():
            f.write(f"\n--- {path} ---\n{summary}\n")

    print("\n✅ Summarization complete. File: file_summaries.txt")

    # Ask if project summary is needed
    ask_summary = input("\nDo you want a high-level project summary as well? (yes/no): ").strip().lower()
    if ask_summary == "yes":
        project_summary = generate_project_summary(file_summaries)
        with open("project_summary.txt", "w", encoding="utf-8") as f:
            f.write(project_summary)
        print("📝 Project summary saved to: project_summary.txt")

        readme_content = generate_readme(project_summary, file_summaries)
        with open("README_GENERATED.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("📄 README_GENERATED.md created.")

    # Q&A session
    print("\nYou can now ask questions about the codebase (summarized or not).")
    while True:
        q = input("\nAsk a question (or type 'exit' to quit): ").strip()
        if q.lower() == 'exit':
            print("Exiting.")
            break
        if not q:
            print("⚠️ Please enter a valid question.")
            continue
        try:
            answer = answer_question(q, file_summaries, repo_path)
            print(f"\nAnswer:\n{answer}")
        except Exception as e:
            print(f"Error while answering: {e}")

if __name__ == "__main__":
    main()
