from PIL import ImageEnhance
import streamlit as st
import torch
import diffusers
from diffusers import StableDiffusionPipeline
import io
import os
import json

device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available() else "cpu"
)

@st.cache_resource
def build_pipeline(model_name: str):
    model_dict = {
        "SD V1.5": "runwayml/stable-diffusion-v1-5",
        "SD Pokemon": "lambdalabs/sd-pokemon-diffusers",
        "SD Dogs": "path/to/fine-tuned-model-2",
    }
    pipeline = StableDiffusionPipeline.from_pretrained(
        model_dict.get(model_name),
        torch_dtype=torch.float16,
        use_safetensors=False,
    ).to(device)
    return pipeline

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