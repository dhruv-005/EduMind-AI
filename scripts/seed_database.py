#!/usr/bin/env python3
"""
Seed the database with demo data for testing.
Run from backend directory: python scripts/seed_database.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from datetime import datetime

def seed():
    print("Seeding EduMind AI database...")

    try:
        from app.core.database import SessionLocal, create_tables
        from app.core.security import hash_password
        from app.models.user import User, UserRole

        create_tables()
        db = SessionLocal()

        # Create demo users
        users_data = [
            {
                "id": str(uuid.uuid4()),
                "email": "admin@edumind.ai",
                "full_name": "Admin User",
                "role": UserRole.ADMIN,
                "password": "admin1234"
            },
            {
                "id": str(uuid.uuid4()),
                "email": "demo@edumind.ai",
                "full_name": "Demo User",
                "role": UserRole.STUDENT,
                "password": "demo1234"
            },
            {
                "id": str(uuid.uuid4()),
                "email": "teacher@edumind.ai",
                "full_name": "Demo Teacher",
                "role": UserRole.TEACHER,
                "password": "teacher1234"
            },
        ]

        for user_data in users_data:
            existing = db.query(User).filter(
                User.email == user_data["email"]
            ).first()

            if not existing:
                user = User(
                    id=user_data["id"],
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    hashed_password=hash_password(
                        user_data["password"]
                    ),
                    is_active=True,
                    is_verified=True,
                    consent_given=True,
                    consent_date=datetime.utcnow()
                )
                db.add(user)
                print(f"  Created user: {user_data['email']}")
            else:
                print(f"  User exists: {user_data['email']}")

        db.commit()
        db.close()

        print("\nDatabase seeded successfully!")
        print("\nDemo accounts:")
        print("  admin@edumind.ai / admin1234 (Admin)")
        print("  demo@edumind.ai / demo1234 (Student)")
        print("  teacher@edumind.ai / teacher1234 (Teacher)")

    except Exception as e:
        print(f"Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    seed()
