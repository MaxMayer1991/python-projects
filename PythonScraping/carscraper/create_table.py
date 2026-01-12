import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_correct_table():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL is not set in environment variables")
    
    print("Connecting to the database...")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        # Create a new table with correct schema
        print("Creating new table with correct schema...")
        
        # First, drop the existing table if it exists
        cur.execute("""
            DROP TABLE IF EXISTS car_products_new;
        """)
        
        # Create the new table with correct schema
        cur.execute("""
            CREATE TABLE car_products_new (
                id SERIAL PRIMARY KEY,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                price_usd INTEGER,
                odometer INTEGER,
                username TEXT,
                phone_number TEXT[],  -- Changed from BIGINT[] to TEXT[]
                image_url TEXT[],
                image_count INTEGER,
                car_number TEXT,
                car_vin TEXT,
                datetime_found TIMESTAMP WITH TIME ZONE,
                datetime_updated TIMESTAMP WITH TIME ZONE
            );
        """)
        
        # Copy data from old table to new table if it exists
        try:
            cur.execute("""
                INSERT INTO car_products_new (
                    id, url, title, price_usd, odometer, username, 
                    phone_number, image_url, image_count, car_number, car_vin, 
                    datetime_found, datetime_updated
                )
                SELECT 
                    id, url, title, price_usd, odometer, username, 
                    ARRAY(SELECT unnest(phone_number)::TEXT), 
                    image_url, image_count, car_number, car_vin, 
                    datetime_found, datetime_updated
                FROM car_products;
            """)
            print("Data copied from old table to new table")
        except Exception as e:
            print(f"Could not copy data from old table (it might not exist): {e}")
        
        # Rename tables to swap them
        cur.execute("""
            DROP TABLE IF EXISTS car_products_old;
            ALTER TABLE IF EXISTS car_products RENAME TO car_products_old;
            ALTER TABLE car_products_new RENAME TO car_products;
        """)
        
        print("Table created successfully with correct schema")
        
    except Exception as e:
        print(f"Error creating table: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
        print("Database connection closed")

if __name__ == "__main__":
    create_correct_table()
