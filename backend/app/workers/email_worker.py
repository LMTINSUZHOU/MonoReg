from rq import Worker

from app.core.database import SessionLocal
from app.services.email_service import process_job_logs
from app.workers.queue import get_redis


def process_email_job(job_id: int) -> None:
    db = SessionLocal()
    try:
        process_job_logs(db, job_id)
    finally:
        db.close()


def main() -> None:
    redis = get_redis()
    worker = Worker(["emails"], connection=redis)
    worker.work()


if __name__ == "__main__":
    main()

