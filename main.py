# Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
# .\venv\Scripts\Activate.ps1
 
import sys
from agent.repo_handler import clone_repo, read_code_files
from agent.summarizer import summarize_repo, generate_project_summary
from agent.readme_generator import generate_readme
from agent.qa import answer_question

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <Github Repo URL>")
        return
    
    repo_url = sys.argv[1]
    repo_path = clone_repo(repo_url)
    code_files = read_code_files(repo_path)
    print(f"Total code files read: {len(code_files)}")
    print("Files:")
    for f in list(code_files.keys())[:5]:
        print(f" - {f}")

    file_summaries = summarize_repo(code_files)
    print(f"Total file summaries generated: {len(file_summaries)}")


    project_summary = generate_project_summary(file_summaries)
    readme_content = generate_readme(project_summary, file_summaries)

    with open("project_summary.txt", "w", encoding="utf-8") as f:
        f.write(project_summary)

    with open("file_summaries.txt", "w", encoding="utf-8") as f:
        for path, summary in file_summaries.items():
            f.write(f"\n--- {path} ---\n{summary}\n")
            print(f"\n--- {path} ---\n{summary}\n")

    with open("README_GENERATED.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("Summarization complete. Outputs saved to:")
    print(" - project_summary.txt")
    print(" - file_summaries.txt")
    print(" - README_GENERATED.md")

    # Interactively ask questions
    print("\n✅ You can now ask questions about the codebase!")
    while True:
        q = input("\nAsk a question (or type 'exit' to quit): ").strip()
        if q.lower() == 'exit':
            print("Exiting Q&A session.")
            break
        if q == "":
            print("⚠️ Please enter a valid question.")
            continue
        try:
            answer = answer_question(q, file_summaries)
            print(f"\nAnswer:\n{answer}")
        except Exception as e:
            print(f"Error while answering: {e}")


if __name__ == "__main__":
    main()
