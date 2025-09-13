"""
Image utilities for Qwen Image API.
"""

import io
import base64
from typing import List, Any
from PIL import Image
import numpy as np
import torch

def tensor_to_base64_image(tensor: torch.Tensor) -> str:
    """
    Convert a tensor to a base64 encoded image.
    
    Args:
        tensor: Image tensor
        
    Returns:
        Base64 encoded image string
    """
    # Convert tensor to PIL Image
    if isinstance(tensor, torch.Tensor):
        # Convert tensor to numpy array
        image_np = tensor.cpu().numpy()
        # If the tensor is in [0, 1] range, convert to [0, 255]
        if image_np.max() <= 1.0:
            image_np = (image_np * 255).astype(np.uint8)
        # If tensor has shape [H, W, C], convert to PIL
        pil_image = Image.fromarray(image_np.squeeze())
    else:
        pil_image = tensor
    
    # Convert PIL image to base64
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def base64_to_tensor_image(base64_string: str) -> torch.Tensor:
    """
    Convert a base64 encoded image to a tensor.
    
    Args:
        base64_string: Base64 encoded image string
        
    Returns:
        Image tensor
    """
    # Decode base64 string
    image_data = base64.b64decode(base64_string)
    
    # Convert to PIL Image
    image = Image.open(io.BytesIO(image_data))
    
    # Convert to tensor
    image_tensor = torch.from_numpy(np.array(image).astype(np.float32) / 255.0)
    image_tensor = image_tensor.unsqueeze(0)  # Add batch dimension
    
    return image_tensor

def prepare_images_for_api(images: List[Any]) -> List[dict]:
    """
    Convert images to format required by API.
    
    Args:
        images: List of images (tensors or PIL Images)
        
    Returns:
        List of dictionaries with image data
    """
    image_data = []
    for i, image in enumerate(images, 1):
        if image is not None:
            base64_image = tensor_to_base64_image(image)
            image_data.append({
                "id": str(i),
                "data": base64_image
            })
    return image_data