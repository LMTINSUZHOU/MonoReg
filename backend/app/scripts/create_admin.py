from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models import AdminUser


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.execute(
            select(AdminUser).where(AdminUser.username == settings.init_admin_username)
        ).scalar_one_or_none()
        if existing:
            print(f"Admin user already exists: {existing.username}")
            return
        user = AdminUser(
            username=settings.init_admin_username,
            email=settings.init_admin_email,
            password_hash=get_password_hash(settings.init_admin_password),
            role="super_admin",
            status="active",
        )
        db.add(user)
        db.commit()
        print(f"Created admin user: {user.username}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

