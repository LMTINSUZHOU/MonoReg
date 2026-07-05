# MonoReg Backend

FastAPI backend for MonoReg. Run migrations first, then create the initial admin:

```bash
alembic upgrade head
python -m app.scripts.create_admin
uvicorn app.main:app --reload
```

The worker entrypoint is:

```bash
python -m app.workers.email_worker
```

