from job_search.src.job_model import Job


def format_jobs(jobs: list[Job]) -> str:
    if not jobs:
        return "No interesting jobs found."

    lines = []
    for job in jobs:
        line = f"- {job.summary}"
        if job.link:
            line += f"\n  {job.link}"
        lines.append(line)

    return "\n\n".join(lines)
