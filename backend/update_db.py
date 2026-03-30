import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_DB = os.getenv("MYSQL_DB", "sorting_quiz")

try:
    connection = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    cursor = connection.cursor()

    # Add new columns if they don't exist
    alter_statements = [
        "ALTER TABLE user ADD COLUMN IF NOT EXISTS username VARCHAR(50) DEFAULT NULL",
        "ALTER TABLE user ADD COLUMN IF NOT EXISTS high_score INT DEFAULT 0",
        "ALTER TABLE user ADD COLUMN IF NOT EXISTS total_games INT DEFAULT 0", 
        "ALTER TABLE user ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE",
        "ALTER TABLE user ADD COLUMN IF NOT EXISTS verification_token VARCHAR(255) DEFAULT NULL",
        "ALTER TABLE user ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255) DEFAULT NULL",
        "ALTER TABLE user ADD COLUMN IF NOT EXISTS reset_token_expires DATETIME DEFAULT NULL"
    ]

    for statement in alter_statements:
        try:
            cursor.execute(statement)
            print(f"✓ Executed: {statement}")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print(f"⚠ Column already exists: {statement}")
            else:
                print(f"✗ Error with {statement}: {e}")

    connection.commit()
    print("\n✅ Database schema updated successfully!")

except Exception as e:
    print(f"❌ Connection error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
