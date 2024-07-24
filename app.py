import uvicorn
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import bcrypt
from utils import User, Image, get_db, create_tables
from fastapi.responses import StreamingResponse
import io
from datetime import datetime

# Create tables when the application starts
create_tables()

app = FastAPI()


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    date_of_birth: str


class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    username: str
    password: str


class ImageResponse(BaseModel):
    id: int
    filename: str
    prompt: str
    created_at: datetime

    class Config:
        orm_mode = True


@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    db_user = User(
        username=user.username,
        hashed_password=hashed_password.decode("utf-8"),
        email=user.email,
        date_of_birth=user.date_of_birth,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login", response_model=UserResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not bcrypt.checkpw(
            user.password.encode("utf-8"), db_user.hashed_password.encode("utf-8")
    ):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return db_user


@app.post("/images/{user_id}")
async def upload_image(
        user_id: int,
        file: UploadFile = File(...),
        prompt: str = Form(...),
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    contents = await file.read()
    db_image = Image(
        filename=file.filename, data=contents, prompt=prompt, owner_id=user_id
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return {"message": "Image uploaded successfully"}


@app.get("/images/{user_id}", response_model=List[ImageResponse])
def get_user_images(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.images


@app.get("/image/{image_id}")
def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return StreamingResponse(io.BytesIO(image.data), media_type="image/png")


@app.delete("/image/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    db.delete(image)
    db.commit()
    return {"message": "Image deleted successfully"}


if __name__ == "__main__":
    uvicorn.run(app)
