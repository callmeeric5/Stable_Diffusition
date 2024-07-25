import streamlit as st
from transformers import pipeline, Conversation
from utils import (
    generate_image,
    apply_adjustments,
    image_to_bytes,
    ui_tab_txt2img,
)
import io
import requests

# Set up the text-generation pipeline for prompt suggestions and chatbot
gpt2_pipe = pipeline('text-generation', model='Gustavosta/MagicPrompt-Stable-Diffusion', tokenizer='gpt2')
chatbot_pipe = pipeline('conversational', model='facebook/blenderbot-400M-distill')

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
    else:
        st.success("Image saved to gallery successfully!")

def get_prompt_suggestions(prompt):
    suggestions = gpt2_pipe(prompt, max_length=50, num_return_sequences=1)
    return suggestions[0]['generated_text']

def chat_with_bot(user_input):
    # Initialize conversation history if not present
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    # Create a Conversation object
    conversation = Conversation(user_input)
    
    # Pass the conversation object to the chatbot pipeline
    conversation = chatbot_pipe(conversation)
    
    # Get the latest response
    if conversation and conversation.generated_responses:
        response = conversation.generated_responses[-1]
        response_text = response['text'] if isinstance(response, dict) else response
    else:
        response_text = "No response generated."

    # Update the conversation history
    st.session_state.conversation_history.append(("You", user_input))
    st.session_state.conversation_history.append(("Bot", response_text))

    return response_text

def home_page():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
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

    tabs = st.tabs(["Generate", "Save", "Chat"])

    with tabs[0]:
        st.session_state.active_tab = "Text to Image"
        model_name, prompt, height, width = ui_tab_txt2img()

        # Prompt Suggestions
        with st.expander("Prompt Suggestions"):
            suggested_prompt = get_prompt_suggestions(prompt)
            st.write("Suggested Prompt:")
            st.write(suggested_prompt)

        if st.button(
            "Generate", key="txt2img", type="primary", use_container_width=True
        ):
            with st.spinner("Generating image..."):
                generated_image = generate_image(model_name, prompt, height, width)
                st.session_state.generated_image = generated_image
                st.session_state.adjusted_image = generated_image.copy()
                st.session_state.prompt = prompt
                image_placeholder = st.empty()
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
                    save_to_gallery_api(
                        st.session_state.adjusted_image,
                        st.session_state.current_user["id"],
                        st.session_state.prompt,
                    )

    with tabs[2]:
        st.session_state.active_tab = "Chat"
        st.header("Chat with our Bot")

        # Initialize chat history if not present
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []

        user_input = st.text_input("You:", "")
        if user_input:
            response = chat_with_bot(user_input)
            st.text_area(
                "Chat History", 
                value="\n".join([f"{speaker}: {message}" for speaker, message in st.session_state.conversation_history]),
                height=300, 
                max_chars=None, 
                key="chat_history"
            )

if __name__ == "__main__":
    home_page()
