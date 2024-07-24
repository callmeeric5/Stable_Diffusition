import streamlit as st
import os
import json
from PIL import Image
import io
import math
from utils import image_to_bytes


def gallery():
    if not st.session_state.logged_in:
        st.warning("Please log in to access this page.")
        st.stop()
    st.title("Gallery")

    # Get list of images and metadata files
    images = sorted([f for f in os.listdir("gallery/images") if f.endswith(".png")])
    metadata_files = sorted(
        [f for f in os.listdir("gallery/metadata") if f.endswith(".json")]
    )

    if not images:
        st.warning("No images in the gallery.")
        return

    # Sidebar
    with st.sidebar:
        st.header("Gallery Controls")

        # Layout selection
        layout = st.selectbox("Select layout", ["3x3", "3x2"])
        rows, cols = (3, 3) if layout == "3x3" else (3, 2)
        items_per_page = rows * cols

        # Pagination variables
        total_pages = math.ceil(len(images) / items_per_page)

        # Page selection
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)

        st.write(f"Page {page} of {total_pages}")

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous") and page > 1:
                page -= 1
        with col2:
            if st.button("Next") and page < total_pages:
                page += 1

    # Calculate start and end indices for current page
    start = (page - 1) * items_per_page
    end = start + items_per_page

    # Display images and options in a grid layout
    for i in range(start, min(end, len(images)), cols):
        row = st.columns(cols)
        for j in range(cols):
            if i + j < len(images):
                image_path = os.path.join("gallery/images", images[i + j])
                metadata_path = os.path.join("gallery/metadata", metadata_files[i + j])

                with row[j]:
                    image = load_image(image_path)
                    image = scale_image(
                        image, 300, 300
                    )  # Scale image to 300x300 for display
                    st.image(image, use_column_width=True)
                    metadata = load_metadata(metadata_path)
                    st.text(f"Prompt: {metadata['prompt']}")
                    st.download_button(
                        label="Download",
                        data=image_to_bytes(image),
                        file_name=images[i + j],
                        mime="image/png",
                        use_container_width=True,
                    )
                    if st.button(f"Delete", key=f"delete_{i + j}"):
                        delete_image(image_path, metadata_path)
                        st.success(f"Deleted {images[i + j]}")
                        st.rerun()


def load_image(path):
    return Image.open(path)


def load_metadata(path):
    with open(path, "r") as f:
        return json.load(f)


def delete_image(image_path, metadata_path):
    os.remove(image_path)
    os.remove(metadata_path)


def image_to_bytes(image):
    if image is None:
        return None
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()


def scale_image(image, max_width, max_height):
    # Maintain aspect ratio
    aspect_ratio = min(max_width / image.width, max_height / image.height)
    new_width = int(image.width * aspect_ratio)
    new_height = int(image.height * aspect_ratio)
    return image.resize((new_width, new_height), Image.LANCZOS)


if __name__ == "__main__":
    gallery()
