import streamlit as st
import requests
from io import BytesIO
from PIL import Image

# Define prompt suggestions for each category
prompts_data = {
    "Dog": [
        "A playful dog running in a park",
        "A dog wearing a funny costume",
        "A dog playing fetch with a ball",
        "A dog lying on a cozy bed",
        "A dog with a bone in its mouth"
    ],
    "Cat": [
        "A cat lounging in a sunbeam",
        "A cat playing with a feather toy",
        "A cat hiding in a box",
        "A cat sitting on a windowsill",
        "A cat chasing a laser pointer"
    ],
    "Pokemon": [
        "A Pikachu using Thunderbolt",
        "A Charizard flying over a volcano",
        "A Bulbasaur in a grassy field",
        "A Jigglypuff singing a lullaby",
        "A Squirtle in a water fight"
    ]
}

def generate_image(prompt):
    # Replace with your model's API URL
    api_url = "http://your-model-endpoint/generate"
    
    # Set up the payload for your model
    payload = {
        "prompt": prompt
    }
    
    # Make the request to your model
    response = requests.post(api_url, json=payload)
    response.raise_for_status()  # Handle any request errors

    # Return the image data
    image_data = response.content
    return image_data

# Title of the app
st.title("Custom Image Generation")

# Sidebar for category selection and suggested prompts
st.sidebar.title("Select a Category")
category = st.sidebar.selectbox("Choose a category", options=list(prompts_data.keys()))

# Display suggested prompts in the sidebar if a category is selected
# Display suggested prompts in the sidebar if a category is selected
if category:
    st.sidebar.title("Suggested Prompts")
    st.sidebar.write(f"Here are some prompt suggestions for {category} to get you started 🤩")
    for prompt in prompts_data[category]:
        if st.sidebar.button(prompt, key=prompt):
            st.session_state.selected_prompt = prompt
            st.session_state.is_custom_prompt = False

            # Generate and display the image for the selected prompt
            image_data = generate_image(prompt)
            st.sidebar.write("Generated Image:")
            img = Image.open(BytesIO(image_data))
            st.sidebar.image(img)

# Main page for custom prompt input
st.write("## 🎉Play with Your Own Prompt 🎉")

# Use text_area for a larger input box with a playful hint
custom_prompt = st.text_area(
    "Enter your custom prompt here:",
    height=300
)

if custom_prompt:
    st.session_state.selected_prompt = custom_prompt
    st.session_state.is_custom_prompt = True
    st.write(f"Generating image for your custom prompt: {custom_prompt}")

    # Generate and display the image for the custom prompt
    image_data = generate_image(custom_prompt)
    st.write("Generated Image:")
    img = Image.open(BytesIO(image_data))
    st.image(img)

# Display the selected prompt
if 'selected_prompt' in st.session_state:
    st.write("Selected Prompt:")
    st.text_area("Prompt", value=st.session_state.selected_prompt, height=100)
