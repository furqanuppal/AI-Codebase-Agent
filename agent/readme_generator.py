def generate_readme(project_summary, file_summaries):
    readme = '# Project Overview\n\n'
    readme += f'{project_summary}\n\n'

    readme += '# File Summaries\n'

    for path, summary in file_summaries.items():
        short_path = path.split('/')[-1]

        readme += f'### {short_path}\n{summary}\n\n'

    return readme
