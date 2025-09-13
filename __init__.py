"""
ComfyUI_Qwen_Image - A custom node for ComfyUI that integrates Qwen-Image models
for text-to-image and image-to-image editing.
"""

from .qwen_image.nodes.t2i_generator import QwenT2IGenerator
from .qwen_image.nodes.i2i_editor import QwenI2IGenerator

NODE_CLASS_MAPPINGS = {
    "QwenT2IGenerator": QwenT2IGenerator,
    "QwenI2IGenerator": QwenI2IGenerator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenT2IGenerator": "Qwen Text-to-Image Generator",
    "QwenI2IGenerator": "Qwen Image-to-Image Editor",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']