"""
Backward compatibility module - imports Qwen nodes from their new separate modules.
"""

from .qwen_image.t2i_generator import QwenT2IGenerator
from .qwen_image.i2i_generator import QwenI2IGenerator
from .qwen.vl_generator import QwenVLGenerator

# For backward compatibility, we re-export the classes
__all__ = ['QwenT2IGenerator', 'QwenI2IGenerator', 'QwenVLGenerator']