"""
Image-to-image editing node for Qwen Image API.
"""

import torch
import requests
import io
import numpy as np
from PIL import Image
from typing import Tuple, Optional
from ..api.client import QwenAPIClient
from ..utils.image_utils import tensor_to_base64_image
from ..utils.config import QwenAPIConfig
from ..exceptions import QwenAPIError

class QwenI2IGenerator:
    """Node for image-to-image editing using Qwen-Image-Edit model."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Edit this image"
                }),
                "image": ("IMAGE",)
            },
            "optional": {
                "mask_image": ("IMAGE",),
                "negative_prompt": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "watermark": ("BOOLEAN", {
                    "default": False
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "image_url")
    FUNCTION = "edit"
    CATEGORY = "Ru4ls/QwenImage"
    
    def __init__(self):
        """Initialize the node with API client."""
        try:
            config = QwenAPIConfig()
            self.api_client = QwenAPIClient(config)
        except Exception as e:
            print(f"Failed to initialize QwenI2IGenerator: {e}")
            self.api_client = None
    
    def edit(self, prompt: str, image: torch.Tensor, 
             mask_image: Optional[torch.Tensor] = None,
             negative_prompt: str = "", watermark: bool = False) -> Tuple[torch.Tensor, str]:
        """
        Edit an image based on text instructions.
        
        Args:
            prompt: Text instruction for editing the image
            image: Input image tensor to edit
            mask_image: Mask image tensor defining areas to edit (optional)
            negative_prompt: Text describing content to avoid
            watermark: Add Qwen-Image watermark to output
            
        Returns:
            Tuple of (image tensor, image URL)
        """
        if not self.api_client:
            raise RuntimeError("API client not initialized. Check your configuration.")
        
        try:
            # Convert images to base64
            image_base64 = tensor_to_base64_image(image)
            mask_base64 = tensor_to_base64_image(mask_image) if mask_image is not None else None
            
            # Edit image using API client
            image_url = self.api_client.edit_image(
                prompt=prompt,
                image_data=image_base64,
                mask_data=mask_base64,
                negative_prompt=negative_prompt,
                watermark=watermark
            )
            
            # Download the edited image
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
            raise RuntimeError(f"Failed to edit image: {str(e)}")