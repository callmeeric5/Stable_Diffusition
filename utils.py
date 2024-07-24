from PIL import ImageEnhance
import streamlit as st
import torch
import diffusers
from diffusers import StableDiffusionPipeline, DiffusionPipeline, AutoencoderKL
import io
import os
import json
import bcrypt


def signup(username, password, email, date_of_birth):
    if username in st.session_state.users:
        return False
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    st.session_state.users[username] = hashed_password
    return True


def login(username, password):
    if username not in st.session_state.users:
        return False
    hashed_password = st.session_state.users[username]
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


def init_session_state():
    if 'users' not in st.session_state:
        st.session_state.users = {}
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_user' not in st.session_state:
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
            'runwayml/stable-diffusion-v1-5',
            torch_dtype=torch.float16,
            use_safetensors=False,
        ).to(device)
    elif model_name == "SD Pokemon":
        return StableDiffusionPipeline.from_pretrained(
            'lambdalabs/sd-pokemon-diffusers',
            torch_dtype=torch.float16,
            use_safetensors=False,
        ).to(device)
    elif model_name == "SD Dogs":
        vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
        pipe = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            vae=vae,
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True
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
        "Pokemon": "A Pikachu using Thunderbolt",
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
