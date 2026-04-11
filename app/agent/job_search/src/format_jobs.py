from job_search.src.job_model import Job


def format_jobs(jobs: list[Job]) -> str:
    if not jobs:
        return "No interesting jobs found."

    blocks = []
    for job in jobs:
        block = f"id: {job.public_id}\n{job.summary}"
        if job.link:
            block += f"\n{job.link}"
        blocks.append(block)

    separator = "\n###############\n"
    return separator.join(blocks)
