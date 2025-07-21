from agent.analyzer import client, deployment_name

def answer_question(question, file_summaries):
    combined = "\n".join(
        f"{path}:\n{summary}" for path, summary in file_summaries.items()
    )

    prompt = f"""
Your are a smart AI code assistant. Based on the following code summaries, answer the user's question.

Codebase summaries:
{combined[:500000000]}

Question:
{question}
"""
    
    response = client.chat.completions.create(
        model = deployment_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2500
    )

    return response.choices[0].message.content.strip()
