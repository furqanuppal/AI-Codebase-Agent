from agent.analyzer import summarize_code
from openai import AzureOpenAI
from agent.analyzer import deployment_name, client

def summarize_repo(code_files):
    summaries = {}
    for file_path, code in code_files.items():
        print(f"📄 Summarizing {file_path} ({len(code)} characters)...")

        summary = summarize_code(file_path, code)

        if summary.strip():
            print("✅ Summary generated.")
        else:
            print("❌ Empty summary returned.")

        summaries[file_path] = summary
    return summaries

def generate_project_summary(file_summaries):
    if not file_summaries:
        return ""
    
    combined = '\n'.join(file_summaries.values())
    prompt = f'''
You are an AI Software Analyst. Based on the following file summaries, generate a high-level summary of the entire project. Write it in 2 paragraphs max.

File Summaries:
{combined[:8000]}
'''
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=700
    )
    
    print("\nGPT raw response:")
    print(response)

    if not response.choices or not response.choices[0].message:
        return "No summary returned by GPT."
    
    summary = response.choices[0].message.content.strip()

    print("\n--- Project Summary ---")
    print(summary)
    
    return summary
