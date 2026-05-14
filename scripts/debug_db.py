import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.database.postgres import init_postgres, get_db
from sqlalchemy import text

init_postgres()

print(f"Connecting to: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
print(f"Database: {settings.POSTGRES_DB}")
print(f"User: {settings.POSTGRES_USER}")

db = next(get_db())
result = db.execute(text("SELECT current_database()")).fetchone()
print(f"Connected to database: {result[0]}")

result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")).fetchall()
print(f"Tables found: {len(result)}")
for table in result:
    print(f"  - {table[0]}")