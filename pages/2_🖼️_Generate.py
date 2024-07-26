import streamlit as st
from utils import (
    generate_image,
    apply_adjustments,
    image_to_bytes,
    ui_tab_txt2img,
)
import io
import requests

st.set_page_config(page_title="Home", layout="wide")
API_URL = st.secrets["API_URL"]


def save_to_gallery_api(image, user_id, prompt):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()

    files = {"file": ("image.png", img_byte_arr, "image/png")}
    data = {"prompt": prompt}
    response = requests.post(f"{API_URL}/images/{user_id}", files=files, data=data)

    if response.status_code != 200:
        st.error("Failed to save image to gallery")


def home_page():
    if not st.session_state.logged_in:
        st.warning("Please log in to access this page.")
        st.stop()
    # Initialize session state variables
    if "generated_image" not in st.session_state:
        st.session_state.generated_image = None
    if "adjusted_image" not in st.session_state:
        st.session_state.adjusted_image = None
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Text to Image"

    st.title("Home")

    # Create a container with a fixed height
    main_container = st.container(height=550)

    with main_container:
        main_cols = st.columns([3, 1])

        with main_cols[0]:
            image_placeholder = st.empty()
            if st.session_state.adjusted_image:
                image_placeholder.image(st.session_state.adjusted_image)

        with main_cols[1]:
            brightness = st.slider(
                "Brightness", 0.0, 2.0, 1.0, 0.1, key="brightness_slider"
            )
            contrast = st.slider("Contrast", 0.0, 2.0, 1.0, 0.1, key="contrast_slider")
            saturation = st.slider(
                "Saturation", 0.0, 2.0, 1.0, 0.1, key="saturation_slider"
            )

            if st.session_state.generated_image:
                adjusted_image = apply_adjustments(
                    st.session_state.generated_image.copy(),
                    brightness,
                    contrast,
                    saturation,
                )
                st.session_state.adjusted_image = adjusted_image
                image_placeholder.image(adjusted_image)

    tabs = st.tabs(["Generate", "Save"])

    with tabs[0]:
        st.session_state.active_tab = "Text to Image"
        model_name, prompt, height, width = ui_tab_txt2img()

        if st.button(
            "Generate", key="txt2img", type="primary", use_container_width=True
        ):
            with st.spinner("Generating image..."):
                generated_image = generate_image(model_name, prompt, height, width)
                st.session_state.generated_image = generated_image
                st.session_state.adjusted_image = generated_image.copy()
                st.session_state.prompt = prompt
                image_placeholder.image(generated_image)

    with tabs[1]:
        st.session_state.active_tab = "Save"
        if st.session_state.adjusted_image is None:
            st.warning("No image generated yet. Please generate an image first.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="Download Image",
                    data=image_to_bytes(st.session_state.adjusted_image),
                    file_name="generated_image.png",
                    mime="image/png",
                    use_container_width=True,
                )

            with col2:
                if st.button("Save to Gallery", use_container_width=True):
                    # save_to_gallery(
                    #     st.session_state.adjusted_image, st.session_state.prompt
                    # )
                    save_to_gallery_api(
                        st.session_state.adjusted_image,
                        st.session_state.current_user["id"],
                        st.session_state.prompt,
                    )
                    st.success("Image saved to gallery successfully!")


if __name__ == "__main__":
    home_page()
