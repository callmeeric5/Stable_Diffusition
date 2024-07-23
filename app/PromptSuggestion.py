import requests
from io import BytesIO
from PIL import Image

class ImageGenerator:
    def __init__(self, api_url):
        self.api_url = api_url
        self.prompts_data = {
            "Dog": [
                "A playful dog running in a park",
                "A dog wearing a funny costume",
            ],
            "Cat": [
                "A cat lounging in a sunbeam",
                "A cat playing with a feather toy",
            ],
            "Pokemon": [
                "A Pikachu using Thunderbolt",
                "A Charizard flying over a volcano",
            ]
        }

    def generate_image(self, prompt):
        """Send a request to the image generation model and return the image data."""
        payload = {"prompt": prompt}
        response = requests.post(self.api_url, json=payload)
        response.raise_for_status()  # Handle any request errors
        image_data = response.content
        return image_data

    def get_image_for_prompt(self, category, custom_prompt=None):
        """Generate an image based on the category or a custom prompt."""
        if category not in self.prompts_data:
            raise ValueError("Invalid category. Please select a valid category.")
        
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompts = self.prompts_data[category]
            prompt = prompts[0]  # Example: Choose the first prompt for simplicity
        
        image_data = self.generate_image(prompt)
        img = Image.open(BytesIO(image_data))
        return img
