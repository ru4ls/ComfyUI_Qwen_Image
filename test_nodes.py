import sys
import os

# Add the current directory to the path so we can import the nodes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Test importing from the new structure
    from qwen_image.nodes.t2i_generator import QwenT2IGenerator
    from qwen_image.nodes.i2i_editor import QwenI2IGenerator
    
    # Test that the classes can be imported
    t2i_node = QwenT2IGenerator()
    i2i_node = QwenI2IGenerator()
    
    # Check the RETURN_TYPES
    print("QwenT2IGenerator.RETURN_TYPES:", t2i_node.RETURN_TYPES)
    print("QwenT2IGenerator.RETURN_NAMES:", getattr(t2i_node, 'RETURN_NAMES', 'Not defined'))
    
    print("QwenI2IGenerator.RETURN_TYPES:", i2i_node.RETURN_TYPES)
    print("QwenI2IGenerator.RETURN_NAMES:", getattr(i2i_node, 'RETURN_NAMES', 'Not defined'))
    
    print("All tests passed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()