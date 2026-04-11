from job_search.src.job_repository import JobRepository


class LikeJob:
    def __init__(self, job_repo: JobRepository):
        self._job_repo = job_repo

    async def like(self, public_id: str) -> None:
        updated = await self._job_repo.update_liked_by_user_by_public_id(
            public_id=public_id, liked_by_user=True
        )
        if not updated:
            raise ValueError(f"job with public_id {public_id} not found")
