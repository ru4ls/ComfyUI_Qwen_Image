from ..core.api_base import QwenAPIBase
import json
import requests
from PIL import Image
import numpy as np
import torch
import io

class QwenI2IGenerator(QwenAPIBase):
    """Node for image-to-image editing using Qwen-Image-Edit model"""
    
    REGION_OPTIONS = [
        "international",
        "mainland_china"
    ]
    
    def __init__(self):
        super().__init__()
        self.model = "qwen-image-edit"  # Fixed model for this node
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Edit this image"
                }),
                "image": ("IMAGE",),
                "region": (cls.REGION_OPTIONS, {
                    "default": "international"
                })
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
    
    def edit(self, prompt, image, region, mask_image=None, negative_prompt="", watermark=False):
        # Check API key based on region
        api_key = self.check_api_key(region)
        
        # Get the appropriate API URL based on region
        api_url = self.get_api_url(region)
        
        # Debug: Print API key status
        print(f"Using API key: {api_key[:8]}...{api_key[-4:]}")
        print(f"Selected model: {self.model}")
        print(f"Using API endpoint: {api_url}")
        print(f"Selected region: {region}")
        
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
            "Authorization": f"Bearer {api_key}",
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
            print(f"Making API request to {api_url}")
            response = requests.post(api_url, headers=headers, json=payload)
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