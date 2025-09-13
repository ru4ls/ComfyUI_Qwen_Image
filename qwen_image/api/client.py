"""
API client for Qwen Image models.
"""

import json
import requests
from typing import Dict, Any, Optional
from .config import QwenAPIConfig
from ..exceptions import QwenAPIAuthenticationError, QwenAPIRequestError, QwenAPIResponseError

class QwenAPIClient:
    """API client for Qwen Image models."""
    
    def __init__(self, config: Optional[QwenAPIConfig] = None):
        """
        Initialize API client.
        
        Args:
            config: Configuration object. If None, will create a default one.
        """
        self.config = config or QwenAPIConfig()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "DISABLE"
        })
    
    def generate_image(self, prompt: str, size: str = "1328*1328", 
                      negative_prompt: str = "", prompt_extend: bool = True,
                      watermark: bool = False, seed: int = 0) -> str:
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
            URL of generated image
            
        Raises:
            QwenAPIAuthenticationError: If authentication fails
            QwenAPIRequestError: If request fails
            QwenAPIResponseError: If response cannot be processed
        """
        payload = {
            "model": "qwen-image",
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
            
        try:
            response = self.session.post(self.config.t2i_api_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Extract image URL from response
            if "output" in result and "choices" in result["output"]:
                choices = result["output"]["choices"]
                if len(choices) > 0 and "message" in choices[0] and "content" in choices[0]["message"]:
                    content = choices[0]["message"]["content"]
                    if len(content) > 0 and "image" in content[0]:
                        return content[0]["image"]
            
            raise QwenAPIResponseError(f"Unexpected API response format: {result}")
            
        except requests.exceptions.RequestException as e:
            self._handle_request_exception(e)
    
    def edit_image(self, prompt: str, image_data: str, mask_data: Optional[str] = None,
                  negative_prompt: str = "", watermark: bool = False) -> str:
        """
        Edit an image based on text instructions.
        
        Args:
            prompt: Text instruction for editing the image
            image_data: Base64 encoded image data
            mask_data: Base64 encoded mask data (optional)
            negative_prompt: Text describing content to avoid
            watermark: Add Qwen-Image watermark to output
            
        Returns:
            URL of edited image
            
        Raises:
            QwenAPIAuthenticationError: If authentication fails
            QwenAPIRequestError: If request fails
            QwenAPIResponseError: If response cannot be processed
        """
        content = [
            {
                "image": f"data:image/png;base64,{image_data}"
            },
            {
                "text": prompt
            }
        ]
        
        # Add mask if provided
        if mask_data:
            content.insert(1, {
                "mask": f"data:image/png;base64,{mask_data}"
            })
        
        payload = {
            "model": "qwen-image-edit",
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
            
        try:
            response = self.session.post(self.config.i2i_api_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Extract image URL from response
            if "output" in result and "choices" in result["output"]:
                choices = result["output"]["choices"]
                if len(choices) > 0 and "message" in choices[0] and "content" in choices[0]["message"]:
                    content = choices[0]["message"]["content"]
                    if len(content) > 0 and "image" in content[0]:
                        return content[0]["image"]
            
            raise QwenAPIResponseError(f"Unexpected API response format: {result}")
            
        except requests.exceptions.RequestException as e:
            self._handle_request_exception(e)
    
    def _handle_request_exception(self, e: requests.exceptions.RequestException) -> None:
        """Handle request exceptions and raise appropriate custom exceptions."""
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            response_text = e.response.text
            
            if status_code == 401:
                raise QwenAPIAuthenticationError(
                    f"API request failed: 401 Unauthorized. "
                    f"This usually means your API key is invalid or not properly configured. "
                    f"Error details: {response_text}"
                )
            elif status_code == 403:
                raise QwenAPIAuthenticationError(
                    f"API request failed: 403 Forbidden. "
                    f"This usually means your API key is valid but you don't have access to this model. "
                    f"Error details: {response_text}"
                )
            elif status_code == 400:
                raise QwenAPIRequestError(
                    f"API request failed: 400 Bad Request. "
                    f"This usually means there's an issue with the request format. "
                    f"Error details: {response_text}"
                )
            else:
                raise QwenAPIRequestError(
                    f"API request failed: {status_code} {e.response.reason}. Response: {response_text}"
                )
        else:
            raise QwenAPIRequestError(f"API request failed: {str(e)}")