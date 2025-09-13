"""
Tests for Qwen Image ComfyUI nodes.
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add the current directory to the path so we can import the nodes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qwen_image.nodes.t2i_generator import QwenT2IGenerator
from qwen_image.nodes.i2i_editor import QwenI2IGenerator
from qwen_image.utils.config import QwenAPIConfig
from qwen_image.exceptions import QwenAPIConfigurationError

def test_t2i_node_import():
    """Test that the T2I node can be imported."""
    t2i_node = QwenT2IGenerator()
    assert t2i_node is not None

def test_i2i_node_import():
    """Test that the I2I node can be imported."""
    i2i_node = QwenI2IGenerator()
    assert i2i_node is not None

def test_node_return_types():
    """Test that nodes have correct return types."""
    t2i_node = QwenT2IGenerator()
    i2i_node = QwenI2IGenerator()
    
    assert hasattr(t2i_node, 'RETURN_TYPES')
    assert hasattr(t2i_node, 'RETURN_NAMES')
    assert hasattr(i2i_node, 'RETURN_TYPES')
    assert hasattr(i2i_node, 'RETURN_NAMES')

@patch('qwen_image.utils.config.load_dotenv')
def test_config_without_api_key(mock_load_dotenv):
    """Test configuration without API key raises error."""
    mock_load_dotenv.return_value = None
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(QwenAPIConfigurationError):
            QwenAPIConfig()

def test_t2i_node_input_types():
    """Test T2I node input types."""
    input_types = QwenT2IGenerator.INPUT_TYPES()
    assert 'required' in input_types
    assert 'prompt' in input_types['required']
    assert 'size' in input_types['required']

def test_i2i_node_input_types():
    """Test I2I node input types."""
    input_types = QwenI2IGenerator.INPUT_TYPES()
    assert 'required' in input_types
    assert 'prompt' in input_types['required']
    assert 'image' in input_types['required']