import google.generativeai as genai
import os

# Configure with your API key
genai.configure(api_key="AIzaSyCXOqoHLVyHwfV9yoLoj66eyj62s8WhsAs")

# List all available models
print("Available Models:")
for model in genai.list_models():
    # Filter for models that support content generation
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")