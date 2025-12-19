import os
import tempfile
import io
from typing import Optional, Union, Any
import httpx
from google import genai
from huggingface_hub import InferenceClient
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# === PROVIDER CONFIGURATION ===
# Supported providers: 'huggingface' (free), 'openai' (paid), 'replicate' (paid)
GENERATION_PROVIDER = os.getenv("GENERATION_PROVIDER", "huggingface")  # Default to free tier
VISION_PROVIDER = "google_gemini"  # Currently only Gemini is supported

def initialize_generation_client(provider: Optional[str] = None) -> Any:
    """
    Initialize image generation client based on provider.
    Supports: huggingface (free), openai (paid), replicate (paid)
    """
    if provider is None:
        provider = GENERATION_PROVIDER
    
    if provider == "huggingface":
        return InferenceClient(
            model="stabilityai/stable-diffusion-xl-base-1.0", 
            token=os.getenv("HF_TOKEN")
        )
    elif provider == "openai":
        # Add OpenAI client when API key is available
        try:
            from openai import OpenAI
            return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    else:
        raise ValueError(f"Unsupported provider: {provider}")

# --- PART 1: VISION (Google Gemini) ---
def analyze_image(image_url: str, prompt_type: str = "caption", custom_question: Optional[str] = None) -> str:
    """
    Analyzes an image using Google Gemini 1.5 Flash.
    
    Args:
        image_url: URL of the image to analyze
        prompt_type: Type of analysis ('caption', 'detection', 'vqa')
        custom_question: Custom question for VQA (optional)
    """
    # Define the user prompt based on the feature
    if prompt_type == "caption":
        user_prompt = "Describe this image in a concise, human-readable sentence."
    elif prompt_type == "detection":
        user_prompt = "List the primary objects present in this image. Return them as a comma-separated list."
    elif prompt_type == "vqa":
        if custom_question:
            user_prompt = custom_question
        else:
            user_prompt = "Answer the question related to this image."
    else:
        user_prompt = "What is in this image?"

    try:
        # Download the image to a temporary file
        response = httpx.get(image_url)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(response.content)
            tmp_file_path = tmp_file.name

        try:
            # Use the new Gemini API pattern with API key
            client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            my_file = client.files.upload(file=tmp_file_path)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[my_file, user_prompt],
            )
            return response.text if response.text is not None else ""
        finally:
            # Clean up temp file
            os.unlink(tmp_file_path)
    except Exception as e:
        print(f"Gemini Vision Error: {e}")
        return "Error analyzing image."

# --- PART 2: GENERATION (Multi-Provider Support) ---
def generate_image_from_text(
    prompt: str, 
    task: str = "text-to-image", 
    image_url: Optional[str] = None, 
    provider: Optional[str] = None
) -> Optional[Image.Image]:
    """
    Generates an image using the configured provider (HuggingFace, OpenAI).
    
    Args:
        prompt: Text prompt for generation or variation
        task: "text-to-image" or "image-variation"
        image_url: URL of the source image (required for image-variation)
        provider: Override default provider ('huggingface', 'openai')
    
    Returns:
        PIL Image object or None on error
        
    Note:
        For FREE tier (HuggingFace), image-variation uses a smart workaround:
        1. Analyze source image with Gemini to get detailed description
        2. Combine description with user's style prompt
        3. Generate new image with combined prompt
        
        For PAID tier (OpenAI), true img2img is used.
    """
    try:
        if provider is None:
            provider = GENERATION_PROVIDER
        
        client = initialize_generation_client(provider)
        
        image = None
        
        if task == "text-to-image":
            # Simple text-to-image generation
            if provider == "huggingface":
                image = client.text_to_image(prompt)
            elif provider == "openai":
                # OpenAI DALL-E 3
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                # Download image from URL
                img_response = httpx.get(response.data[0].url)
                image = Image.open(io.BytesIO(img_response.content))
            else:
                raise NotImplementedError(f"Provider {provider} not yet implemented")
        
        elif task == "image-variation":
            if not image_url:
                raise ValueError("image_url is required for image-variation task")
            
            if provider == "huggingface":
                # FREE TIER WORKAROUND: Use Gemini to analyze + text-to-image
                print("🔄 Using smart variation (Free tier: Gemini analysis + Stable Diffusion)")
                
                # Step 1: Analyze the source image
                base_description = analyze_image(image_url, prompt_type="caption")
                print(f"📝 Analyzed image: {base_description}")
                
                # Step 2: Combine with user's style/modification prompt
                combined_prompt = f"{base_description}. {prompt}"
                print(f"🎨 Combined prompt: {combined_prompt}")
                
                # Step 3: Generate new image
                image = client.text_to_image(combined_prompt)
                
            elif provider == "openai":
                # OpenAI DALL-E variations (TRUE image-to-image)
                print("🎨 Using DALL-E variations (Paid tier)")
                img_download = httpx.get(image_url)
                img_download.raise_for_status()
                
                # DALL-E requires PNG format and size constraints
                dalle_response = client.images.create_variation(
                    image=img_download.content,
                    n=1,
                    size="1024x1024"
                )
                img_response = httpx.get(dalle_response.data[0].url)
                image = Image.open(io.BytesIO(img_response.content))
                
            else:
                raise NotImplementedError(f"Image variation for {provider} not yet implemented")
        else:
            raise ValueError(f"Invalid task type: {task}. Must be 'text-to-image' or 'image-variation'")
        
        return image
    except Exception as e:
        # Get provider from local scope or use default
        error_provider = provider if provider else GENERATION_PROVIDER
        print(f"❌ Generation Error ({error_provider}): {e}")
        return None
