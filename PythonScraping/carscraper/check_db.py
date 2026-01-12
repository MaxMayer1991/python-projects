import os
import sys
import psycopg2
from dotenv import load_dotenv

# Set console output encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def test_connection():
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    print(f"Testing connection to: {db_url}")
    
    try:
        # Test basic connection
        print("\n1. Testing basic connection...")
        conn = psycopg2.connect(db_url, connect_timeout=5)
        print("[SUCCESS] Connected to PostgreSQL")
        
        # Test query
        print("\n2. Testing query execution...")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"[SUCCESS] PostgreSQL version: {version[0]}")
        
        # Check if table exists
        print("\n3. Checking if table 'car_products' exists...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'car_products'
            );
        """)
        table_exists = cur.fetchone()[0]
        print(f"[INFO] Table exists: {table_exists}")
        
        if table_exists:
            # Check table structure
            print("\n4. Checking table structure...")
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'car_products';
            """)
            print("\nTable columns:")
            for col in cur.fetchall():
                print(f"- {col[0]}: {col[1]}")
        
        cur.close()
        conn.close()
        print("\n[SUCCESS] All tests completed successfully!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n[ERROR] Connection failed: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure PostgreSQL is running")
        print("2. Verify the DATABASE_URL in your .env file is correct")
        print("3. Check if the database server is accessible from your network")
        print("4. If using Docker, ensure the container is running and ports are properly mapped")
        print("5. Check if the port (default: 5432) is open and not blocked by firewall")
    except psycopg2.ProgrammingError as e:
        print(f"\n[ERROR] SQL Error: {e}")
        print("\nThis might be a permission issue or the database might not exist.")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
    
    return False

if __name__ == "__main__":
    test_connection()
