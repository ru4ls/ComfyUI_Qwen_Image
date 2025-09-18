"""
ComfyUI_Qwen - A custom node for ComfyUI that provides seamless integration
with the Qwen multimodal models from Alibaba Cloud Model Studio.
"""

# Import all nodes
from .qwen_image_nodes import *

# This is the entry point for ComfyUI to discover our nodes
NODE_CLASS_MAPPINGS = {
    "QwenT2IGenerator": QwenT2IGenerator,
    "QwenI2IGenerator": QwenI2IGenerator,
    "QwenVLGenerator": QwenVLGenerator,
}

# Display names for the nodes in the ComfyUI interface
NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenT2IGenerator": "Qwen Text-to-Image Generator",
    "QwenI2IGenerator": "Qwen Image-to-Image Editor",
    "QwenVLGenerator": "Qwen Vision-Language Generator",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']