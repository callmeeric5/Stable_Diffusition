import streamlit as st
from PIL import Image
import io
import math
import requests
from datetime import datetime

API_URL = st.secrets["API_URL"]

def gallery():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Please log in to access this page.")
        st.stop()

    st.title("Gallery")

    # Fetch images for the current user
    user_id = st.session_state.current_user["id"]
    response = requests.get(f"{API_URL}/images/{user_id}")
    if response.status_code != 200:
        st.error("Failed to fetch images")
        return

    images = response.json()

    if not images:
        st.warning("No images in the gallery.")
        return

    # Initialize page state if not already
    if "page" not in st.session_state:
        st.session_state.page = 1

    # Sidebar
    with st.sidebar:
        st.header("Gallery Controls")

        # Layout selection
        layout = st.selectbox("Select layout", ["3x3", "3x2"])
        rows, cols = (3, 3) if layout == "3x3" else (3, 2)
        items_per_page = rows * cols

        # Sorting
        sort_option = st.selectbox("Sort by", ["Newest", "Oldest"])

        # Sort images based on 'created_at' if available, otherwise use 'id'
        if images and "created_at" in images[0]:
            images.sort(
                key=lambda x: datetime.fromisoformat(x["created_at"]),
                reverse=(sort_option == "Newest"),
            )
        else:
            st.warning("'created_at' field not available. Sorting by ID instead.")
            images.sort(key=lambda x: x["id"], reverse=(sort_option == "Newest"))

        # Pagination variables
        total_pages = math.ceil(len(images) / items_per_page)

        # Page selection
        st.session_state.page = st.number_input("Page", min_value=1, max_value=total_pages, value=st.session_state.page)

        st.write(f"Page {st.session_state.page} of {total_pages}")

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous") and st.session_state.page > 1:
                st.session_state.page -= 1
                st.experimental_rerun()
        with col2:
            if st.button("Next") and st.session_state.page < total_pages:
                st.session_state.page += 1
                st.experimental_rerun()

    # Calculate start and end indices for current page
    start = (st.session_state.page - 1) * items_per_page
    end = start + items_per_page

    # Display images and options in a grid layout
    for i in range(start, min(end, len(images)), cols):
        row = st.columns(cols)
        for j in range(cols):
            if i + j < len(images):
                image = images[i + j]
                with row[j]:
                    # Fetch and display the image
                    image_response = requests.get(f"{API_URL}/image/{image['id']}")
                    if image_response.status_code == 200:
                        img = Image.open(io.BytesIO(image_response.content))
                        st.image(img, use_column_width=True)

                        # Display prompt with expansion option
                        prompt = image.get("prompt", "No prompt available")

                        with st.expander("Detail"):
                            st.write(prompt)
                            created_at = image.get("created_at", "Not available")
                            created_at = datetime.fromisoformat(
                                created_at.rstrip("Z")
                            ).strftime("%Y-%m-%d %H:%M")

                            st.markdown(
                                f"<small>Created: {created_at}</small>",
                                unsafe_allow_html=True,
                            )

                        # Add to Favorites
                        if st.button(f"Favorite", key=f"favorite_{image['id']}"):
                            toggle_favorite(image["id"])
                            st.success(f"Toggled favorite for {image['filename']}")
                            st.experimental_rerun()

                        # Rate the Image
                        rating = st.slider(f"Rate this image", 1, 5, key=f"rating_{image['id']}")
                        if st.button(f"Submit Rating", key=f"submit_rating_{image['id']}"):
                            submit_rating(image["id"], rating)
                            st.success(f"Rating submitted for {image['filename']}")
                            st.experimental_rerun()

                        if st.button(f"Delete", key=f"delete_{image['id']}"):
                            delete_image(image["id"])
                            st.success(f"Deleted {image['filename']}")
                            st.experimental_rerun()
                    else:
                        st.error(f"Failed to load image {image['filename']}")

def toggle_favorite(image_id):
    # Implement toggle favorite logic
    response = requests.post(f"{API_URL}/image/{image_id}/favorite")
    if response.status_code != 200:
        st.error("Failed to toggle favorite status")

def submit_rating(image_id, rating):
    # Implement submit rating logic
    response = requests.post(f"{API_URL}/image/{image_id}/rate", json={"rating": rating})
    if response.status_code != 200:
        st.error("Failed to submit rating")

def delete_image(image_id):
    response = requests.delete(f"{API_URL}/image/{image_id}")
    if response.status_code != 200:
        st.error("Failed to delete image")

if __name__ == "__main__":
    gallery()
