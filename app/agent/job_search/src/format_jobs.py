from job_search.src.job_model import Job


def format_jobs(jobs: list[Job]) -> str:
    if not jobs:
        return "No interesting jobs found."

    blocks = []
    for index, job in enumerate(jobs, start=1):
        block = f"{index}. id: {job.public_id}\n{job.summary}"
        if job.link:
            block += f"\n{job.link}"
        blocks.append(block)

    separator = "\n###############\n"
    return separator.join(blocks)
