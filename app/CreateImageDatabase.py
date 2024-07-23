import psycopg2

IMG_DB_PARAMS = {
    'dbname': 'ImageGenerated',
    'user': 'postgres',
    'password': 'fangliyang12',
    'host': 'localhost',
    'port': 5432
}

def create_image_table():
    conn = psycopg2.connect(**IMG_DB_PARAMS)
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_images (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    image BYTEA NOT NULL,
                    prompt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            conn.commit()
            print("Table 'user_images' created successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error creating table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_image_table()
