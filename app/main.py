from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

# Database connection parameters
DB_PARAMS = {
    'dbname': 'user_auth_db',
    'user': 'preethapallavi',
    'password': '1111',
    'host': 'localhost',
    'port': 5433
}

# JWT Secret Key and Expiration
JWT_SECRET = 'your_jwt_secret'
EXPIRATION_DELTA = timedelta(hours=1)

# OAuth2 password bearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db_connection():
    conn = psycopg2.connect(**DB_PARAMS)
    return conn

class User(BaseModel):
    username: str
    email: str
    password: str
    date_of_birth: str  # Use str for date

class LoginUser(BaseModel):
    identifier: str  # Can be username or email
    password: str

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.post('/signup')
async def signup(user: User):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO users (username, email, password_hash, date_of_birth) VALUES (%s, %s, %s, %s)',
                (user.username, user.email, hashed_password, user.date_of_birth)
            )
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f'Error creating user: {e}')
    finally:
        conn.close()
    return {'message': 'User created successfully'}

@app.post('/login')
async def login(user: LoginUser):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Fetch user by username or email
            cursor.execute(
                'SELECT username, password_hash FROM users WHERE username = %s OR email = %s',
                (user.identifier, user.identifier)
            )
            db_user = cursor.fetchone()

            if db_user is None:
                raise HTTPException(status_code=401, detail='User not found')

            username, hashed_password = db_user

            # Verify the password
            if bcrypt.checkpw(user.password.encode('utf-8'), hashed_password.encode('utf-8')):
                # Create JWT token
                expiry = datetime.utcnow() + EXPIRATION_DELTA
                token = jwt.encode({'username': username, 'exp': expiry}, JWT_SECRET, algorithm='HS256')
                return {'token': token}
            else:
                raise HTTPException(status_code=401, detail='Invalid credentials')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error logging in: {e}')
    finally:
        conn.close()

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "This is a protected route", "user": current_user}
