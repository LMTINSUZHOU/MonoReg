from datetime import datetime, timedelta

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.encryption import encrypt_text
from app.models import Account, Activity, EmailJob, EmailLog, EmailTemplate, FormField, Registration
from app.services.form_service import CORE_FIELDS


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.execute(select(Activity).where(Activity.slug == "demo-competition")).scalar_one_or_none()
        if existing:
            print("Demo activity already exists")
            return
        activity = Activity(
            title="2026 新生程序设计竞赛",
            slug="demo-competition",
            description="用于验证 MonoReg 报名、账号和邮件流程的示例活动。",
            status="open",
            start_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now() + timedelta(days=30),
            max_registrations=300,
            need_account=True,
            auto_generate_account=True,
            send_confirm_email=False,
            send_account_email_immediately=False,
            login_url="https://oj.example.com",
        )
        db.add(activity)
        db.flush()
        fields = CORE_FIELDS + [
            {
                "field_key": "school",
                "field_label": "学校",
                "field_type": "text",
                "required": True,
                "placeholder": "请输入学校",
                "help_text": "",
                "options_json": [],
                "validation_json": {},
                "show_in_table": True,
                "sort_order": 4,
            },
            {
                "field_key": "grade",
                "field_label": "年级",
                "field_type": "select",
                "required": False,
                "placeholder": "",
                "help_text": "",
                "options_json": ["大一", "大二", "大三", "大四"],
                "validation_json": {},
                "show_in_table": True,
                "sort_order": 5,
            },
        ]
        for field in fields:
            db.add(FormField(activity_id=activity.id, **field))
        db.add(
            EmailTemplate(
                activity_id=activity.id,
                name="报名确认邮件",
                type="registration_confirm",
                subject="{{活动名称}} 报名确认",
                body="同学你好，{{姓名}}：\n\n你已成功报名 {{活动名称}}。\n\n请妥善保留本邮件。",
            )
        )
        db.add(
            EmailTemplate(
                activity_id=activity.id,
                name="账号通知邮件",
                type="account_info",
                subject="{{活动名称}} 账号信息",
                body="同学你好，{{姓名}}：\n\n账号：{{账号}}\n密码：{{密码}}\n登录地址：{{登录地址}}\n\n请提前登录平台测试账号是否可用。",
            )
        )
        registrations = [
            Registration(
                activity_id=activity.id,
                name="张三",
                email="zhangsan@example.com",
                phone="13800000000",
                status="account_ready",
                form_data={"school": "示例大学", "grade": "大一"},
            ),
            Registration(
                activity_id=activity.id,
                name="李四",
                email="lisi@example.com",
                phone="13900000000",
                status="approved",
                form_data={"school": "示例学院", "grade": "大二"},
            ),
            Registration(
                activity_id=activity.id,
                name="王五",
                email="wangwu@example.com",
                phone="13700000000",
                status="pending",
                form_data={"school": "测试大学", "grade": "大三"},
            ),
        ]
        db.add_all(registrations)
        db.flush()
        db.add(
            Account(
                activity_id=activity.id,
                registration_id=registrations[0].id,
                username="acm2026_0001",
                password_encrypted=encrypt_text("DemoPass123"),
                status="ready",
            )
        )
        job = EmailJob(
            activity_id=activity.id,
            job_type="registration_confirm",
            status="completed",
            total_count=2,
            success_count=2,
            failed_count=0,
        )
        db.add(job)
        db.flush()
        for registration in registrations[:2]:
            db.add(
                EmailLog(
                    job_id=job.id,
                    activity_id=activity.id,
                    registration_id=registration.id,
                    to_email=registration.email,
                    subject="2026 新生程序设计竞赛 报名确认",
                    body_snapshot="同学你好，你已成功报名。",
                    status="sent",
                )
            )
        db.commit()
        print("Created demo activity: demo-competition")
    finally:
        db.close()


if __name__ == "__main__":
    main()
