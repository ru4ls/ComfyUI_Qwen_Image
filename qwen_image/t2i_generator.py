from ..core.api_base import QwenAPIBase
import json
import requests
from PIL import Image
import numpy as np
import torch
import io

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
    
    REGION_OPTIONS = [
        "international",
        "mainland_china"
    ]
    
    def __init__(self):
        super().__init__()
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
                }),
                "region": (cls.REGION_OPTIONS, {
                    "default": "international"
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
    
    def generate(self, prompt, size, region, negative_prompt="", prompt_extend=True, watermark=False, seed=0):
        # Check API key based on region
        api_key = self.check_api_key(region)
        
        # Get the appropriate API URL based on region
        api_url = self.get_api_url(region)
        
        # Debug: Print API key status
        print(f"Using API key: {api_key[:8]}...{api_key[-4:]}")
        print(f"Selected model: {self.model}")
        print(f"Using API endpoint: {api_url}")
        print(f"Selected region: {region}")
        
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
            "Authorization": f"Bearer {api_key}",
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