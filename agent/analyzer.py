import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key="*****************************************",
    api_version="************",
    azure_endpoint="********************************"
)

deployment_name = "gpt-4o"

def summarize_code(file_path, code):
    if not code.strip():
        return ""
    
    prompt = f'''
You are an expert software engineer. Read the following code and explain what it does in simple terms.

Filename: {os.path.basename(file_path)}

Code:
{code[:10000]}

Provide:
1. Summary of file purpose
2. Any major functions or logic
3. Any possible issues or code smells
'''
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[{'role': 'user', 'content': prompt}],
        temperature = 0.3,
        max_tokens = 700
    )

    print("\nGPT raw response:")
    print(response)

    summary_text = response.choices[0].message.content.strip()

    print(f"\n--- Summary for {os.path.basename(file_path)} ---")
    print(summary_text)

    print(f"🧠 Summary from GPT for {file_path}:\n{summary_text}")

    return summary_text

