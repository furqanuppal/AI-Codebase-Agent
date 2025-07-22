import streamlit as st
import tempfile
import os
from agent.repo_handler import clone_repo, read_code_files, filter_files_by_path
from agent.summarizer import summarize_repo, generate_project_summary
from agent.readme_generator import generate_readme
from agent.qa import answer_question

@st.cache_resource
def clone_and_read(repo_url):
    repo_path = clone_repo(repo_url)
    code_files = read_code_files(repo_path)
    return repo_path, code_files

st.set_page_config(page_title="AI Codebase Agent", layout="wide")
st.title("🧠 AI Codebase Agent")

repo_url = st.text_input("Enter GitHub Repository URL:")

if repo_url:
    with st.spinner("Cloning and reading repository..."):
        repo_path, code_files = clone_and_read(repo_url)
        st.success(f"✅ Cloned and loaded {len(code_files)} readable text files.")
    
    # Ask user what they want to summarize
    summary_scope = st.text_input("🔍 What do you want to summarize?", value="")

    # Text log box for progress
    log_box = st.empty()

    if st.button("Generate / Regenerate Summary") or "file_summaries" not in st.session_state:
        with st.spinner("Generating summaries..."):

            # Determine which files to summarize
            if summary_scope.strip().lower() == "all":
                selected_files = code_files
            else:
                selected_files = filter_files_by_path(code_files, summary_scope)
                if not selected_files:
                    st.error(f"⚠️ No matching files found for '{summary_scope}'. Please try again.")
                    st.stop()

            # Log output
            logs = []
            summaries = {}

            for i, (path, code) in enumerate(selected_files.items(), 1):
                short_path = os.path.relpath(path, repo_path)
                logs.append(f"🔄 [{i}/{len(selected_files)}] Summarizing: `{short_path}`")
                log_box.code("\n".join(logs[-10:]))  # only show last 10 updates
                try:
                    from agent.analyzer import summarize_code
                    summary = summarize_code(path, code)
                    summaries[path] = summary
                    logs.append(f"✅ Done: {short_path}")
                except Exception as e:
                    logs.append(f"❌ Failed: {short_path} — {str(e)}")

            st.session_state["file_summaries"] = summaries

            project_summary = generate_project_summary(summaries)
            st.session_state["project_summary"] = project_summary

            readme = generate_readme(project_summary, summaries)
            st.session_state["readme"] = readme

            log_box.code("\n".join(logs[-20:]))

        st.success("✅ Summaries generated!")

    if "project_summary" in st.session_state:
        st.subheader("📄 Project Summary")
        st.markdown(st.session_state["project_summary"])

        st.subheader("💬 Ask Questions")
        user_question = st.text_input("Ask a question about the codebase")
        if user_question:
            with st.spinner("Thinking..."):
                from agent.qa import answer_question
                answer = answer_question(
                    user_question,
                    st.session_state["file_summaries"],
                    full_repo_path=repo_path
                )
                st.markdown(f"**Answer:** {answer}")

        st.subheader("📥 Download Files")

        def write_temp_file(content, filename):
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(content)
            return temp_path

        file_summaries_path = write_temp_file(
            "\n\n".join(
                [f"{os.path.relpath(file, repo_path)}:\n{summary}" for file, summary in st.session_state["file_summaries"].items()]
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
            "📄 Download File Summaries",
            data=open(file_summaries_path, "rb"),
            file_name="file_summaries.txt",
            mime="text/plain"
        )

        st.download_button(
            "📄 Download Project Summary",
            data=open(project_summary_path, "rb"),
            file_name="project_summary.txt",
            mime="text/plain"
        )

        st.download_button(
            "📘 Download Generated README",
            data=open(readme_path, "rb"),
            file_name="README_GENERATED.md",
            mime="text/markdown"
        )
