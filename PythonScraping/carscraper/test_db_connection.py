import psycopg2
from dotenv import load_dotenv
import os
import sys

# Set console output encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

def test_connection():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        print("[SUCCESS] Connection successful!")
        print(f"Test query result: {result}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
