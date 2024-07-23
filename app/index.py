from PIL import Image, ImageEnhance
import streamlit as st
import torch
import diffusers
from diffusers import StableDiffusionPipeline

st.set_page_config(page_title='Home', layout='wide')
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"


@st.cache_resource
def build_pipeline(model_name: str):
    model_dict = {
        'SD V1.5': 'runwayml/stable-diffusion-v1-5',
        'SD Pokemon': 'lambdalabs/sd-pokemon-diffusers',
        'SD Dogs': 'path/to/fine-tuned-model-2'
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
        negative_prompt=['lowres, bad anatomy, extra digit, fewer digits, cropped, worst quality, low quality'],
        generator=rng,
    ).images

    return images[0]


def apply_adjustments(image: Image.Image, brightness: float, contrast: float, saturation: float) -> Image.Image:
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)

    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(saturation)

    return image


def home_page():


    if st.session_state.get('page', None) != 'Home':
        st.cache_resource.clear()
        torch.cuda.empty_cache()
    st.session_state.page = 'Home'

    st.title('Home')
    main_cols = st.columns([3, 1])

    with main_cols[0]:
        with st.container(border=True, height=520):
            image_placeholder = st.empty()

    with main_cols[1]:
        brightness = st.slider("Brightness", 0.0, 2.0, 1.0, 0.1)
        contrast = st.slider("Contrast", 0.0, 2.0, 1.0, 0.1)
        saturation = st.slider("Saturation", 0.0, 2.0, 1.0, 0.1)

    tabs = st.tabs(["Text to Image"])
    with tabs[0]:
        model_name, prompt, height, width, bttn_txt2img = ui_tab_txt2img()

    if bttn_txt2img:
        st.session_state.generated_image = generate_image(model_name, prompt, height, width)
        adjusted_image = apply_adjustments(st.session_state.generated_image, brightness, contrast, saturation)
        image_placeholder.image(adjusted_image)

    if 'generated_image' in st.session_state:
        adjusted_image = apply_adjustments(st.session_state.generated_image, brightness, contrast, saturation)
        image_placeholder.image(adjusted_image)


def ui_tab_txt2img():
    cols = st.columns(2)
    with cols[0]:
        prompt = st.text_area('Prompt', value='A photo of a cat', height=200)
    with cols[1]:
        model_name = st.selectbox(
            'Model Selection',
            options=[
                'SD V1.5',
                'SD Pokemon',
                'SD Dogs',
            ]
        )
        height = st.slider("Height", min_value=128, max_value=1024, value=512, step=128)
        width = st.slider("Width", min_value=128, max_value=1024, value=512, step=128)

    bttn_txt2img = st.button('Generate', key='txt2img', type='primary', use_container_width=True)

    return model_name, prompt, height, width, bttn_txt2img


def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Gallery"])

    if page == "Home":

        home_page()
    elif page == "Gallery":
        import gallery
        gallery.gallery()


if __name__ == '__main__':
    main()
