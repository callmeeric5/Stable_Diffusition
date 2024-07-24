from PIL import ImageEnhance
import streamlit as st
import torch
import diffusers
from diffusers import StableDiffusionPipeline, DiffusionPipeline, AutoencoderKL
import io
import os
import json
import bcrypt
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    LargeBinary,
    ForeignKey,
    Date,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import requests
import datetime
from sqlalchemy.orm import Session

API_URL = st.secrets["API_URL"]


def signup(username, password, email, date_of_birth):
    # Convert date_of_birth to string
    date_of_birth_str = (
        date_of_birth.isoformat()
        if isinstance(date_of_birth, datetime.date)
        else date_of_birth
    )

    response = requests.post(
        f"{API_URL}/users/",
        json={
            "username": username,
            "password": password,
            "email": email,
            "date_of_birth": date_of_birth_str,
        },
    )
    if response.status_code == 200:
        return True
    return False


def login(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if user and bcrypt.checkpw(
        password.encode("utf-8"), user.hashed_password.encode("utf-8")
    ):
        return user
    return None


def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None


def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None


device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available() else "cpu"
)


@st.cache_resource
def build_pipeline(model_name: str):
    if model_name == "SD V1.5":
        return StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16,
            use_safetensors=False,
        ).to(device)
    elif model_name == "SD Pokemon":
        return StableDiffusionPipeline.from_pretrained(
            "lambdalabs/sd-pokemon-diffusers",
            torch_dtype=torch.float16,
            use_safetensors=False,
        ).to(device)
    elif model_name == "SD Dogs":
        vae = AutoencoderKL.from_pretrained(
            "madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16
        )
        pipe = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            vae=vae,
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True,
        )
        pipe.load_lora_weights("whydelete/husky_lora")
        return pipe.to(device)
    else:
        return None


def generate_image(model_name: str, prompt: str, height: int, width: int):
    pipeline = build_pipeline(model_name)
    pipeline.scheduler = diffusers.PNDMScheduler.from_config(pipeline.scheduler.config)

    rng = torch.Generator(device=device).manual_seed(10)
    images = pipeline(
        prompt=[prompt],
        height=height,
        width=width,
        num_inference_steps=20,
        guidance_scale=7.5,
        negative_prompt=[
            "lowres, bad anatomy, extra digit, fewer digits, cropped, worst quality, low quality"
        ],
        generator=rng,
    ).images

    return images[0]


def apply_adjustments(image, brightness, contrast, saturation):
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)

    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(saturation)

    return image


def image_to_bytes(image):
    if image is None:
        return None
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()


def save_to_gallery(image, prompt):
    if not os.path.exists("gallery/images"):
        os.makedirs("gallery/images")
    if not os.path.exists("gallery/metadata"):
        os.makedirs("gallery/metadata")

    # Save image
    image_count = len(os.listdir("gallery/images"))
    image_path = f"gallery/images/image_{image_count + 1}.png"
    image.save(image_path)

    # Save metadata
    metadata = {"prompt": prompt, "image_path": image_path}
    with open(f"gallery/metadata/metadata_{image_count + 1}.json", "w") as f:
        json.dump(metadata, f)


def ui_tab_txt2img():
    prompt_dict = {
        "Dog": "A playful dog running in a park",
        "Cat": "A cat lounging in a sunbeam",
        "Pokemon": "A Pikachu on the grass",
    }
    cols = st.columns(2)
    with cols[0]:
        category = st.selectbox("Category", options=list(prompt_dict.keys()))
        prompt = st.text_area("Prompt", value=prompt_dict[category], height=150)
    with cols[1]:
        model_name = st.selectbox(
            "Model Selection",
            options=[
                "SD V1.5",
                "SD Pokemon",
                "SD Dogs",
            ],
        )
        height = st.slider("Height", min_value=128, max_value=1024, value=512, step=128)
        width = st.slider("Width", min_value=128, max_value=1024, value=512, step=128)

    return model_name, prompt, height, width


DATABASE_URL = st.secrets["DATABASE_URL"]
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String)
    date_of_birth = Column(Date)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    images = relationship("Image", back_populates="owner")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    data = Column(LargeBinary)
    prompt = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="images")


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


create_tables()
