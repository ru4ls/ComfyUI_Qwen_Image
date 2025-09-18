from ..core.api_base import QwenAPIBase
import json
import requests
from PIL import Image
import numpy as np
import torch
import io
import base64

class QwenVLGenerator(QwenAPIBase):
    """
    Node for Qwen-VL models (qwen-vl-max, qwen-vl-plus) 
    for image understanding and description tasks
    """
    
    MODEL_OPTIONS = [
        "qwen-vl-max",
        "qwen-vl-plus",
        "qwen-vl-max-latest",
        "qwen-vl-plus-latest"
    ]
    
    REGION_OPTIONS = [
        "international",
        "mainland_china"
    ]
    
    def __init__(self):
        super().__init__()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "What is in this picture?"
                }),
                "model": (cls.MODEL_OPTIONS, {
                    "default": "qwen-vl-max"
                }),
                "region": (cls.REGION_OPTIONS, {
                    "default": "international"
                })
            },
            "optional": {
                "stream": ("BOOLEAN", {
                    "default": False
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("description",)
    FUNCTION = "describe"
    CATEGORY = "Ru4ls/Qwen"
    
    def describe(self, image, prompt, model, region, stream=False):
        # Check API key based on region
        api_key = self.check_api_key(region)
        
        # Using OpenAI-compatible endpoint for Qwen-VL models
        api_url = self.get_openai_api_url(region)
        
        # Debug: Print API key status
        print(f"Using API key: {api_key[:8]}...{api_key[-4:]}")
        print(f"Selected model: {model}")
        print(f"Using API endpoint: {api_url}")
        print(f"Selected region: {region}")
        
        # Prepare image data
        image_data = self.prepare_images([image])
        image_base64 = image_data[0]["data"] if image_data else None
        
        # Prepare content for the message
        content = []
        if image_base64:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}"
                }
            })
        
        content.append({
            "type": "text",
            "text": prompt
        })
        
        # Prepare API payload
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "stream": stream
        }
        
        # Set headers for OpenAI-compatible API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Debug: Print request details
        print(f"Request headers: {{'Authorization': 'Bearer {api_key[:8]}...', 'Content-Type': 'application/json'}}")
        print(f"Request payload model: {payload['model']}")
        print(f"Request payload prompt: {prompt[:100]}...")
        print(f"Has image data: {image_base64 is not None}")
        
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
            
            # Extract description from response
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    description = choice["message"]["content"]
                    return (description,)
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