from sqlmodel import Session, select

from models import Job


class JobRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_job_id(self, job_id: str) -> Job | None:
        return self.session.exec(select(Job).where(Job.job_id == job_id)).first()

    def exists(self, job_id: str) -> bool:
        return self.find_by_job_id(job_id) is not None

    def find_all_interesting(self) -> list[Job]:
        return list(self.session.exec(
            select(Job).where(Job.of_interest == True, Job.is_dead == False)
        ).all())

    def save(self, job: Job) -> Job:
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job
