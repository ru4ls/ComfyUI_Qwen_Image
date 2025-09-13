"""
Text-to-image generation node for Qwen Image API.
"""

import torch
import requests
import io
import numpy as np
from PIL import Image
from typing import Tuple
from ..api.client import QwenAPIClient
from ..utils.config import QwenAPIConfig
from ..exceptions import QwenAPIError

class QwenT2IGenerator:
    """Node for text-to-image generation using Qwen-Image model."""
    
    # Define allowed sizes for Qwen-Image models with descriptive names
    SIZE_OPTIONS = [
        "1664*928",  # 16:9 landscape
        "1472*1140", # 4:3 landscape
        "1328*1328", # 1:1 square (default)
        "1140*1472", # 3:4 portrait
        "928*1664"   # 9:16 portrait
    ]
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Generate an image of a cat"
                }),
                "size": (cls.SIZE_OPTIONS, {
                    "default": "1328*1328"
                })
            },
            "optional": {
                "negative_prompt": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "prompt_extend": ("BOOLEAN", {
                    "default": True
                }),
                "watermark": ("BOOLEAN", {
                    "default": False
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 2147483647
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "image_url")
    FUNCTION = "generate"
    CATEGORY = "Ru4ls/QwenImage"
    
    def __init__(self):
        """Initialize the node with API client."""
        try:
            config = QwenAPIConfig()
            self.api_client = QwenAPIClient(config)
        except Exception as e:
            print(f"Failed to initialize QwenT2IGenerator: {e}")
            self.api_client = None
    
    def generate(self, prompt, size, negative_prompt="", prompt_extend=True, 
                watermark=False, seed=0) -> Tuple[torch.Tensor, str]:
        """
        Generate an image from text prompt.
        
        Args:
            prompt: Text prompt for image generation
            size: Output image size
            negative_prompt: Text describing content to avoid
            prompt_extend: Enable intelligent prompt rewriting
            watermark: Add Qwen-Image watermark to output
            seed: Random seed for generation
            
        Returns:
            Tuple of (image tensor, image URL)
        """
        if not self.api_client:
            raise RuntimeError("API client not initialized. Check your configuration.")
        
        try:
            # Generate image using API client
            image_url = self.api_client.generate_image(
                prompt=prompt,
                size=size,
                negative_prompt=negative_prompt,
                prompt_extend=prompt_extend,
                watermark=watermark,
                seed=seed
            )
            
            # Download the generated image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Convert to tensor
            image = Image.open(io.BytesIO(image_response.content))
            image_tensor = torch.from_numpy(np.array(image).astype(np.float32) / 255.0)
            image_tensor = image_tensor.unsqueeze(0)  # Add batch dimension
            
            return (image_tensor, image_url)
            
        except QwenAPIError as e:
            raise RuntimeError(f"Qwen API error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate image: {str(e)}")