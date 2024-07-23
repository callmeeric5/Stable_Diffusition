import psycopg2

IMG_DB_PARAMS = {
    'dbname': 'ImageGenerated',
    'user': 'postgres',
    'password': 'fangliyang12',
    'host': 'localhost',
    'port': 5432
}

def get_image_db_connection():
    return psycopg2.connect(**IMG_DB_PARAMS)

def save_image_to_db(username: str, image_data: bytes, prompt: str):
    conn = get_image_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO user_images (username, image, prompt) VALUES (%s, %s, %s)',
                (username, psycopg2.Binary(image_data), prompt)
            )
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_images_from_db(username: str):
    conn = get_image_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT id, prompt, created_at FROM user_images WHERE username = %s ORDER BY created_at DESC',
                (username,)
            )
            images = cursor.fetchall()
            return [{'id': id, 'prompt': prompt, 'created_at': created_at} for id, prompt, created_at in images]
    except Exception as e:
        raise e
    finally:
        conn.close()

def get_image_data_from_db(image_id: int, username: str):
    conn = get_image_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT image FROM user_images WHERE id = %s AND username = %s',
                (image_id, username)
            )
            image_data = cursor.fetchone()
            return image_data[0] if image_data else None
    except Exception as e:
        raise e
    finally:
        conn.close()
