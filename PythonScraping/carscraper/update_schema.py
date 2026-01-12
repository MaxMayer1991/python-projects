import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_database_schema():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL is not set in environment variables")
    
    print("Connecting to the database...")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        # Check current column type
        cur.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'car_products' 
            AND column_name = 'phone_number'
        """)
        current_type = cur.fetchone()[0]
        print(f"Current phone_number type: {current_type}")
        
        if current_type == 'bigint[]':
            print("Updating phone_number column type from bigint[] to text[]...")
            
            # Create a temporary column
            cur.execute("""
                ALTER TABLE car_products 
                ADD COLUMN phone_number_temp text[]
            """)
            
            # Copy and convert data
            cur.execute("""
                UPDATE car_products 
                SET phone_number_temp = array_agg(phone_number::text)
                FROM unnest(phone_number) AS phone_number
                GROUP BY id
            """)
            
            # Drop the old column and rename the new one
            cur.execute("""
                ALTER TABLE car_products 
                DROP COLUMN phone_number,
                RENAME COLUMN phone_number_temp TO phone_number
            """)
            
            print("Successfully updated phone_number column type to text[]")
        else:
            print("phone_number is already of type text[] or another type")
            
    except Exception as e:
        print(f"Error updating schema: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
        print("Database connection closed")

if __name__ == "__main__":
    update_database_schema()
