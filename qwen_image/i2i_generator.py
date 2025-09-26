from ..core.api_base import QwenAPIBase
import json
import requests
from PIL import Image
import numpy as np
import torch
import io

class QwenI2IGenerator(QwenAPIBase):
    """
    Node for image-to-image editing using Qwen-Image-Edit model
    """
    
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
                "image1": ("IMAGE",),
                "region": (cls.REGION_OPTIONS, {
                    "default": "international"
                })
            },
            "optional": {
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
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
    CATEGORY = "Ru4ls/Qwen"
    
    def edit(self, prompt, image1, region, image2=None, image3=None, negative_prompt="", watermark=False):
        # Check API key based on region
        api_key = self.check_api_key(region)
        
        # Get the appropriate API URL based on region
        api_url = self.get_api_url(region)
        
        # Debug: Print API key status
        print(f"Using API key: {api_key[:8]}...{api_key[-4:]}")
        print(f"Selected model: {self.model}")
        print(f"Using API endpoint: {api_url}")
        print(f"Selected region: {region}")
        
        # Prepare image data for all provided images
        images_to_process = [img for img in [image1, image2, image3] if img is not None]
        if not images_to_process:
            raise ValueError("At least one image must be provided")
        
        image_data_list = self.prepare_images(images_to_process)
        
        # Prepare API payload for image-to-image editing
        # According to DashScope documentation, content should contain all images and text
        content = []
        
        # Add all image data to content
        for img_data in image_data_list:
            if img_data and "data" in img_data:
                content.append({
                    "image": f"data:image/png;base64,{img_data['data']}"  # Add data URI prefix
                })
        
        # Add the text prompt to content
        content.append({
            "text": prompt
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
        print(f"Request headers: {{'Authorization': 'Bearer {api_key[:8]}...', 'Content-Type': 'application/json', 'X-DashScope-Async': 'DISABLE'}}")
        print(f"Request payload model: {payload['model']}")
        # Print the last text content (the prompt) for debugging
        text_content = [item for item in payload['input']['messages'][0]['content'] if 'text' in item]
        prompt_text = text_content[0]['text'] if text_content else "No text prompt found"
        print(f"Request payload prompt: {prompt_text[:100]}...")
        # Count the number of images in the request
        image_count = len([item for item in payload['input']['messages'][0]['content'] if 'image' in item])
        print(f"Number of image inputs: {image_count}")
        
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