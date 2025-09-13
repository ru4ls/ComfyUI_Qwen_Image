# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-09-13

### Added
- Both nodes now return image tensors and image URLs
- Enhanced README documentation with image URL output information
- Detailed project structure documentation

### Changed
- Cleaned up deprecated qwen_image_nodes.py file
- Updated test_nodes.py to use new module structure
- Improved CHANGELOG format

### Fixed
- Removed duplicate code versions
- Updated documentation to reflect current implementation

## [1.0.0] - 2025-09-13

### Added
- Initial release of ComfyUI_Qwen_Image nodes
- Text-to-image generation node (QwenT2IGenerator)
- Image-to-image editing node (QwenI2IGenerator)
- Support for Qwen-Image and Qwen-Image-Edit models
- Configuration management with environment variables
- Comprehensive documentation and examples

### Changed
- Refactored project structure to follow Python packaging best practices
- Improved error handling with custom exception classes
- Enhanced code organization with separate modules for API, nodes, and utilities
- Updated dependency management with pyproject.toml and setup.py

### Fixed
- Improved API key handling and validation
- Better error messages for API request failures
- More robust image processing and conversion