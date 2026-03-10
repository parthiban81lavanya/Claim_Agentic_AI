from db.database import SessionLocal, AdminUser
from werkzeug.security import generate_password_hash

db = SessionLocal()

admin = AdminUser(
    email="admin@example.com",
    password_hash=generate_password_hash("admin123"),
    is_superadmin=True
)

db.add(admin)
db.commit()
db.close()

print("Admin user created successfully!")