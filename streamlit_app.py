import streamlit as st
from agent.repo_handler import clone_repo, read_code_files
from agent.summarizer import summarize_repo, generate_project_summary
from agent.readme_generator import generate_readme
from agent.qa import answer_question
import tempfile
import os

@st.cache_resource
def clone_and_read(repo_url):
    repo_path = clone_repo(repo_url)
    code_files = read_code_files(repo_path)
    return code_files

st.set_page_config(page_title="AI Codebase Agent", layout="wide")
st.title("\U0001F9E0 AI Codebase Agent")

repo_url = st.text_input("Enter GitHub Repository URL:")

if repo_url:
    with st.spinner("Cloning and reading repository..."):
        code_files = clone_and_read(repo_url)
        st.success(f"Cloned and loaded {len(code_files)} files.")

    if st.button("Generate / Regenerate Summary") or "file_summaries" not in st.session_state:
        with st.spinner("Generating summaries..."):
            file_summaries = summarize_repo(code_files)
            st.session_state["file_summaries"] = file_summaries
            st.session_state["project_summary"] = generate_project_summary(file_summaries)
            st.session_state["readme"] = generate_readme(
                st.session_state["project_summary"], file_summaries
            )
        st.success("Summaries generated successfully!")

    if "project_summary" in st.session_state:
        st.subheader("\U0001F4C4 Project Summary")
        st.markdown(st.session_state["project_summary"])

        st.subheader("\U0001F4AC Ask Questions")
        user_question = st.text_input("Ask a question about the codebase")
        if user_question:
            with st.spinner("Thinking..."):
                answer = answer_question(user_question, st.session_state["file_summaries"])
                st.markdown(f"**Answer:** {answer}")

        st.subheader("\U0001F4E5 Download Files")

        def write_temp_file(content, filename):
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(content)
            return temp_path

        file_summaries_path = write_temp_file(
            "\n\n".join(
                [f"{file}:\n{summary}" for file, summary in st.session_state["file_summaries"].items()]
            ),
            "file_summaries.txt"
        )

        project_summary_path = write_temp_file(
            st.session_state["project_summary"], "project_summary.txt"
        )

        readme_path = write_temp_file(
            st.session_state["readme"], "README_GENERATED.md"
        )

        st.download_button(
            "Download File Summaries",
            data=open(file_summaries_path, "rb"),
            file_name="file_summaries.txt",
            mime="text/plain"
        )

        st.download_button(
            "Download Project Summary",
            data=open(project_summary_path, "rb"),
            file_name="project_summary.txt",
            mime="text/plain"
        )

        st.download_button(
            "Download Generated README",
            data=open(readme_path, "rb"),
            file_name="README_GENERATED.md",
            mime="text/markdown"
        )
