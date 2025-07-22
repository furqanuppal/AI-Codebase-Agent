# qa.py

import os
from agent.analyzer import client, deployment_name
from agent.repo_handler import read_code_files, filter_files_by_path

def answer_question(question, file_summaries, full_repo_path):
    # Combine available summaries
    combined_summaries = "\n".join(
        f"{path}:\n{summary}" for path, summary in file_summaries.items()
    )

    # Step 1: Ask using summaries
    base_prompt = f"""
You are a smart AI code assistant. Based on the following code summaries, answer the user's question.

Codebase summaries:
{combined_summaries[:10000]}

Question:
{question}
"""
    base_response = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "user", "content": base_prompt}],
        temperature=0.3,
        max_tokens=2000
    )

    base_answer = base_response.choices[0].message.content.strip()

    # Step 2: Check if the user question requires more than summary (basic heuristic)
    keywords = question.lower().split()
    full_code_files = read_code_files(full_repo_path)
    matching_code = {
        path: content for path, content in full_code_files.items()
        if any(kw in path.lower() or kw in content.lower() for kw in keywords)
    }

    # If matching files are found, combine them for a deeper answer
    if matching_code:
        print(f"🔍 Found {len(matching_code)} raw code files related to the question. Augmenting response...")

        relevant_code = "\n".join(
            f"{path}:\n{content[:3000]}" for path, content in matching_code.items()
        )

        refined_prompt = f"""
You are a smart AI code assistant. Based on the code below and the user's question, provide a detailed and accurate answer.

User's Question:
{question}

Relevant Raw Code:
{relevant_code[:12000]}
"""
        refined_response = client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": refined_prompt}],
            temperature=0.3,
            max_tokens=2000
        )

        refined_answer = refined_response.choices[0].message.content.strip()
        return refined_answer

    # Otherwise, return summary-based answer
    return base_answer
