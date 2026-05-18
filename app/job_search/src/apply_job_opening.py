from datetime import date

from job_search.src.job_opening_model import JobOpening
from job_search.src.job_opening_repository import JobOpeningRepository


class ApplyJobOpening:
    def __init__(self, job_opening_repo: JobOpeningRepository):
        self._job_opening_repo = job_opening_repo

    async def apply(
        self,
        uuid: str,
        applied_at: date,
        asked_salary: str,
        application_file_uuid: str,
    ) -> JobOpening:
        job_opening = await self._job_opening_repo.find_by_uuid(uuid=uuid)
        if job_opening is None:
            raise ValueError(f"Job opening not found: {uuid}")

        job_opening.applied = True
        job_opening.applied_at = applied_at
        job_opening.asked_salary = asked_salary
        job_opening.application_file_uuid = application_file_uuid

        return await self._job_opening_repo.save(job_opening=job_opening)
