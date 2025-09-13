import os
import json
import requests
from PIL import Image
import numpy as np
import torch
import io
import base64
from dotenv import load_dotenv
import sys
import pathlib

# Load environment variables from .env file
# Try to load .env file from the current directory first
env_path = pathlib.Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Fallback to default behavior
    load_dotenv()

# Debug: Print environment variable status
api_key = os.getenv('DASHSCOPE_API_KEY')
if api_key:
    # Strip any extra quotes or whitespace
    api_key = api_key.strip().strip('"\'')
    print(f"API Key loaded: {api_key[:8]}...{api_key[-4:]}")  # Print partial key for security
else:
    print("API Key not found in environment variables")


class QwenAPIBase:
    """Base class for Qwen API interactions"""
    
    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        # Strip any extra quotes or whitespace
        if self.api_key:
            self.api_key = self.api_key.strip().strip('"\'')
        print(f"Initialized QwenAPIBase with API key: {self.api_key[:8] if self.api_key else 'None'}...{self.api_key[-4:] if self.api_key else ''}")
        
    def check_api_key(self):
        """Check if API key is set in environment variables"""
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY environment variable not set. "
                             "Please set it before using this node.")
        return self.api_key
    
    def prepare_images(self, images):
        """Convert images to base64 strings for API submission"""
        image_data = []
        for i, image in enumerate(images, 1):
            if image is not None:
                # Convert tensor to PIL Image
                if isinstance(image, torch.Tensor):
                    # Convert tensor to numpy array
                    image_np = image.cpu().numpy()
                    # If the tensor is in [0, 1] range, convert to [0, 255]
                    if image_np.max() <= 1.0:
                        image_np = (image_np * 255).astype(np.uint8)
                    # If tensor has shape [H, W, C], convert to PIL
                    pil_image = Image.fromarray(image_np.squeeze())
                else:
                    pil_image = image
                
                # Convert PIL image to base64
                buffer = io.BytesIO()
                pil_image.save(buffer, format="PNG")
                img_str = base64.b64encode(buffer.getvalue()).decode()
                image_data.append({
                    "id": str(i),
                    "data": img_str
                })
        return image_data


class QwenT2IGenerator(QwenAPIBase):
    """Node for text-to-image generation using Qwen-Image model"""
    
    # Define allowed sizes for Qwen-Image models with descriptive names
    SIZE_OPTIONS = [
        "1664*928",  # 16:9 landscape
        "1472*1140", # 4:3 landscape
        "1328*1328", # 1:1 square (default)
        "1140*1472", # 3:4 portrait
        "928*1664"   # 9:16 portrait
    ]
    
    def __init__(self):
        super().__init__()
        self.api_url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        self.model = "qwen-image"  # Fixed model for this node
    
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
    RETURN_NAMES = ("image", "url")
    FUNCTION = "generate"
    CATEGORY = "Ru4ls/QwenImage"
    
    def generate(self, prompt, size, negative_prompt="", prompt_extend=True, watermark=False, seed=0):
        # Check API key
        self.check_api_key()
        
        # Debug: Print API key status
        print(f"Using API key: {self.api_key[:8]}...{self.api_key[-4:] if self.api_key else 'None'}")
        print(f"Selected model: {self.model}")
        print(f"Using API endpoint: {self.api_url}")
        
        # Prepare API payload for text-to-image generation - using the exact format from reference
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            },
            "parameters": {
                "size": size,
                "prompt_extend": prompt_extend,
                "watermark": watermark
            }
        }
        
        # Add optional parameters if they have non-default values
        if negative_prompt:
            payload["parameters"]["negative_prompt"] = negative_prompt
        if seed > 0:
            payload["parameters"]["seed"] = seed
        
        # Set headers according to DashScope documentation
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "DISABLE"  # Ensure synchronous response
        }
        
        # Debug: Print request details
        print(f"Request headers: {{'Authorization': 'Bearer {self.api_key[:8]}...', 'Content-Type': 'application/json', 'X-DashScope-Async': 'DISABLE'}}")
        print(f"Request payload model: {payload['model']}")
        print(f"Request payload prompt: {payload['input']['messages'][0]['content'][0]['text'][:100]}...")
        print(f"Request payload size: {payload['parameters']['size']}")
        print(f"Request payload prompt_extend: {payload['parameters']['prompt_extend']}")
        print(f"Request payload watermark: {payload['parameters']['watermark']}")
        
        try:
            # Make API request
            print(f"Making API request to {self.api_url}")
            response = requests.post(self.api_url, headers=headers, json=payload)
            print(f"Response status code: {response.status_code}")
            if hasattr(response, 'text'):
                print(f"Response text: {response.text[:500]}...")  # Print first 500 chars
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            print(f"API response received: {json.dumps(result, indent=2)[:200]}...")  # Print first 200 chars
            
            # Check if this is an image generation response
            if "output" in result and "choices" in result["output"]:
                choices = result["output"]["choices"]
                if len(choices) > 0 and "message" in choices[0] and "content" in choices[0]["message"]:
                    content = choices[0]["message"]["content"]
                    if len(content) > 0 and "image" in content[0]:
                        image_url = content[0]["image"]
                        # Download the generated image
                        image_response = requests.get(image_url)
                        image_response.raise_for_status()
                        
                        # Convert to tensor
                        image = Image.open(io.BytesIO(image_response.content))
                        image_tensor = torch.from_numpy(np.array(image).astype(np.float32) / 255.0)
                        image_tensor = image_tensor.unsqueeze(0)  # Add batch dimension
                        
                        return (image_tensor, image_url)
                    else:
                        raise ValueError(f"Unexpected API response format: {result}")
                else:
                    raise ValueError(f"Unexpected API response format: {result}")
            else:
                raise ValueError(f"Unexpected API response format: {result}")
                
        except requests.exceptions.RequestException as e:
            # More detailed error handling
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                response_text = e.response.text
                print(f"API request failed with status {status_code}: {response_text}")
                if status_code == 401:
                    raise RuntimeError(f"API request failed: 401 Unauthorized. "
                                    f"This usually means your API key is invalid or not properly configured. "
                                    f"Error details: {response_text}")
                elif status_code == 403:
                    raise RuntimeError(f"API request failed: 403 Forbidden. "
                                    f"This usually means your API key is valid but you don't have access to this model. "
                                    f"Error details: {response_text}")
                elif status_code == 400:
                    raise RuntimeError(f"API request failed: 400 Bad Request. "
                                    f"This usually means there's an issue with the request format. "
                                    f"Error details: {response_text}")
                else:
                    raise RuntimeError(f"API request failed: {status_code} {e.response.reason}. Response: {response_text}")
            else:
                raise RuntimeError(f"API request failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to process API response: {str(e)}")


class QwenI2IGenerator(QwenAPIBase):
    """Node for image-to-image editing using Qwen-Image-Edit model"""
    
    def __init__(self):
        super().__init__()
        self.api_url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        self.model = "qwen-image-edit"  # Fixed model for this node
    
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
    RETURN_NAMES = ("image", "url")
    FUNCTION = "edit"
    CATEGORY = "Ru4ls/QwenImage"
    
    def edit(self, prompt, image, mask_image=None, negative_prompt="", watermark=False):
        # Check API key
        self.check_api_key()
        
        # Debug: Print API key status
        print(f"Using API key: {self.api_key[:8]}...{self.api_key[-4:] if self.api_key else 'None'}")
        print(f"Selected model: {self.model}")
        print(f"Using API endpoint: {self.api_url}")
        
        # Prepare image data
        image_data = self.prepare_images([image])
        image_base64 = image_data[0]["data"] if image_data else None
        
        # Prepare API payload for image-to-image editing
        content = [
            {
                "image": f"data:image/png;base64,{image_base64}"  # Add data URI prefix
            },
            {
                "text": prompt
            }
        ]
        
        # Add mask if provided
        if mask_image is not None:
            mask_data = self.prepare_images([mask_image])
            mask_base64 = mask_data[0]["data"] if mask_data else None
            if mask_base64:
                content.insert(1, {
                    "mask": f"data:image/png;base64,{mask_base64}"  # Add mask data URI prefix
                })
        
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            },
            "parameters": {
                "watermark": watermark
            }
        }
        
        # Add optional parameters if they have non-default values
        if negative_prompt:
            payload["parameters"]["negative_prompt"] = negative_prompt
        
        # Set headers according to DashScope documentation
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "DISABLE"  # Ensure synchronous response
        }
        
        # Debug: Print request details
        print(f"Request headers: {{'Authorization': 'Bearer {self.api_key[:8]}...', 'Content-Type': 'application/json', 'X-DashScope-Async': 'DISABLE'}}")
        print(f"Request payload model: {payload['model']}")
        print(f"Request payload prompt: {payload['input']['messages'][0]['content'][1]['text'][:100]}...")
        print(f"Has image data: {image_base64 is not None}")
        print(f"Has mask: {mask_image is not None}")
        
        try:
            # Make API request
            print(f"Making API request to {self.api_url}")
            response = requests.post(self.api_url, headers=headers, json=payload)
            print(f"Response status code: {response.status_code}")
            if hasattr(response, 'text'):
                print(f"Response text: {response.text[:500]}...")  # Print first 500 chars
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            print(f"API response received: {json.dumps(result, indent=2)[:200]}...")  # Print first 200 chars
            
            # Check if this is an image generation response
            if "output" in result and "choices" in result["output"]:
                choices = result["output"]["choices"]
                if len(choices) > 0 and "message" in choices[0] and "content" in choices[0]["message"]:
                    content = choices[0]["message"]["content"]
                    if len(content) > 0 and "image" in content[0]:
                        image_url = content[0]["image"]
                        # Download the generated image
                        image_response = requests.get(image_url)
                        image_response.raise_for_status()
                        
                        # Convert to tensor
                        image = Image.open(io.BytesIO(image_response.content))
                        image_tensor = torch.from_numpy(np.array(image).astype(np.float32) / 255.0)
                        image_tensor = image_tensor.unsqueeze(0)  # Add batch dimension
                        
                        return (image_tensor, image_url)
                    else:
                        raise ValueError(f"Unexpected API response format: {result}")
                else:
                    raise ValueError(f"Unexpected API response format: {result}")
            else:
                raise ValueError(f"Unexpected API response format: {result}")
                
        except requests.exceptions.RequestException as e:
            # More detailed error handling
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                response_text = e.response.text
                print(f"API request failed with status {status_code}: {response_text}")
                if status_code == 401:
                    raise RuntimeError(f"API request failed: 401 Unauthorized. "
                                    f"This usually means your API key is invalid or not properly configured. "
                                    f"Error details: {response_text}")
                elif status_code == 403:
                    raise RuntimeError(f"API request failed: 403 Forbidden. "
                                    f"This usually means your API key is valid but you don't have access to this model. "
                                    f"Error details: {response_text}")
                elif status_code == 400:
                    raise RuntimeError(f"API request failed: 400 Bad Request. "
                                    f"This usually means there's an issue with the request format. "
                                    f"Error details: {response_text}")
                else:
                    raise RuntimeError(f"API request failed: {status_code} {e.response.reason}. Response: {response_text}")
            else:
                raise RuntimeError(f"API request failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to process API response: {str(e)}")


# Node class mappings are in __init__.py