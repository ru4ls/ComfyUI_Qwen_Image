# ComfyUI_Qwen_Image

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


A custom node for ComfyUI that provides **seamless integration** with the **Qwen multimodal models** from **Alibaba Cloud Model Studio**. This solution delivers cutting-edge image generation, editing, and vision capabilities directly within ComfyUI.

### Why Choose Alibaba Cloud Model Studio?

This is a direct integration with Alibaba Cloud's Model Studio service, not a third-party wrapper or local model implementation. Benefits include:

- **Enterprise-Grade Infrastructure**: Leverages Alibaba Cloud's battle-tested AI platform serving millions of requests daily
- **State-of-the-Art Models**: Access to the latest Qwen models (qwen-image, qwen-image-edit, qwen-vl-max, qwen-vl-plus) with continuous updates
- **Commercial Licensing**: Properly licensed for commercial use through Alibaba Cloud's terms of service
- **Scalable Architecture**: Handles high-volume workloads with Alibaba Cloud's reliable infrastructure
- **Security Compliance**: Follows Alibaba Cloud's security best practices with secure API key management

## Important: API Costs & Authorization

⚠️ **This is a paid service**: The Qwen models are provided through Alibaba Cloud's commercial API and incur usage costs. You will be billed according to Alibaba Cloud's pricing model based on your usage.

 **Model Authorization Required**: If you're using a non-default workspace or project in Alibaba Cloud, you may need to explicitly authorize access to the models in your DashScope console.

## Features

- Generate images from text (T2I)
- Edit existing images based on text instructions (I2I)
- Multi-image editing support (up to 3 images for advanced editing workflows)
- Analyze and describe images using Qwen-VL models
- Configurable parameters: region, seed, resolution, prompt extension, watermark, negative prompts
- All nodes now return the image URL in addition to the image tensor
- Support for both international and mainland China API endpoints
- Support for separate API keys for different regions
- Automatic environment variable loading from config directory
- Industry-standard directory organization (core, config, generators)
- Powered by Alibaba Cloud's advanced Qwen models

## Installation

1. Clone this repository to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/ru4ls/ComfyUI_Qwen_Image.git
   ```

2. Install the required dependencies:
   ```bash
   pip install -r ComfyUI_Qwen_Image/requirements.txt
   ```


## Setup

### Obtain API Key

1. Visit [Alibaba Cloud Model Studio](https://dashscope.console.aliyun.com/apiKey) to get your API key
2. Create an account if you don't have one
3. Generate a new API key

### Model Authorization (If Using Non-Default Workspace)

If you're using a workspace other than your default workspace, you may need to authorize the models:

1. Go to the [DashScope Model Management Console](https://dashscope.console.aliyun.com/model)
2. Find the models you want to use (`qwen-image`, `qwen-image-edit`, `qwen-vl-max`, `qwen-vl-plus`)
3. Click "Authorize" or "Subscribe" for each model
4. Select your workspace/project if prompted

### Set Environment Variable

You can set up your API keys in one of two ways:

1. **Recommended approach**: Copy the `config/.env.template` file to `config/.env` and replace the placeholders with your actual API keys:
   ```bash
   cp config/.env.template config/.env
   # Edit config/.env to add your API keys
   ```

2. **Alternative approach**: Copy the `config/.env.template` file to `.env` in the project root directory:
   ```bash
   cp config/.env.template .env
   # Edit .env to add your API keys
   ```

For international endpoint only:
```
DASHSCOPE_API_KEY=your_international_api_key_here
```

For both international and mainland China endpoints:
```
DASHSCOPE_API_KEY=your_international_api_key_here
DASHSCOPE_API_KEY_CHINA=your_china_api_key_here
```

If you only provide `DASHSCOPE_API_KEY`, it will be used for both regions. If you provide both, the China-specific key will be used for the mainland China endpoint.

## Usage

### Text-to-Image Generation

1. Add the "Qwen Text-to-Image Generator" node to your workflow
2. Connect a text input with your prompt
3. Configure parameters as needed (size, seed, region, etc.)
4. Execute the node
5. The node now outputs both the generated image and its URL

### Image-to-Image Editing

1. Add the "Qwen Image-to-Image Editor" node to your workflow
2. Connect one or more image inputs (image1 is required, image2 and image3 are optional)
3. Provide a text instruction for editing and set region
4. Execute the node
5. The node now outputs both the edited image and its URL

### Image Analysis with Qwen-VL

1. Add the "Qwen Vision-Language Generator" node to your workflow
2. Connect an image input
3. Provide a text prompt for analysis (e.g., "What is in this picture?")
4. Select the Qwen-VL model (qwen-vl-max or qwen-vl-plus)
5. Execute the node
6. The node outputs a text description of the image

## Node Parameters

### Text-to-Image Generator
- **prompt** (required): The text prompt for image generation
- **size**: Output image resolution (1664×928, 1472×1140, 1328×1328, 1140×1472, 928×1664)
- **negative_prompt**: Text describing content to avoid in the image
- **prompt_extend**: Enable intelligent prompt rewriting for better results
- **seed**: Random seed for generation (0 for random)
- **watermark**: Add Qwen-Image watermark to output
- **region**: Select API endpoint (international or mainland_china)
- **Outputs**: IMAGE (tensor), URL (string)

### Image-to-Image Editor
- **prompt** (required): Text instruction for editing the image
- **image1** (required): Primary input image to edit
- **image2** (optional): Secondary input image for multi-image editing
- **image3** (optional): Tertiary input image for multi-image editing
- **negative_prompt**: Text describing content to avoid in the edited image
- **watermark**: Add Qwen-Image watermark to output
- **region**: Select API endpoint (international or mainland_china)
- **Outputs**: IMAGE (tensor), URL (string)

### Vision-Language Generator
- **image** (required): Input image to analyze
- **prompt** (required): Text prompt for image analysis
- **model**: Select Qwen-VL model (qwen-vl-max, qwen-vl-plus, qwen-vl-max-latest, qwen-vl-plus-latest)
- **region**: Select API endpoint (international or mainland_china)
- **Outputs**: STRING (text description)

## Examples

### Text-only Generation
Prompt: "Generate an image of a dog"

![Text-to-Image Example](media/ComfyUI_Qwen_Image-t2i.png)

### Image Editing
Edit an existing image:
- Original Image: an image of a dog
- Prompt: "the dog is wearing a red t-shirt and a retro glasses while eating the hamburger"

![Image-to-Image Example](media/ComfyUI_Qwen_Image-i2i.png)

### Multi-Image Editing
Combine multiple images for advanced editing:
- Image1: an image of a room
- Image2: an image showing a furniture style
- Prompt: "Apply the furniture style from the second image to the room in the first image"
- Result: A room with the furniture style applied

- Image1: an image of a person
- Image2: an image of a background scene
- Image3: an image of an object to include
- Prompt: "Place the person from the first image into the background scene with the object from the third image"
- Result: A composite image with all elements combined

### Image Analysis
Analyze an image:
- Image: a photo of a dog
- Prompt: "What breed is this dog and what is it doing?"

## Security

The API key is loaded from the `DASHSCOPE_API_KEY` environment variable and never stored in files or code, following Alibaba Cloud security best practices.

## Changelog

### v1.3.0
- Enhanced Image-to-Image Editor with multi-image support (up to 3 images)
- Added image2 and image3 optional inputs to the Qwen Image-to-Image Editor node
- Updated API payload structure to support multi-image editing workflows
- Improved content array handling to accommodate multiple input images
- Enhanced debugging output to show number of image inputs

### v1.2.0
- Added new Qwen-VL generator node for image understanding and description tasks
- Supports qwen-vl-max, qwen-vl-plus, and latest model variants
- Compatible with both international and mainland China API endpoints
- Enhanced error handling with detailed error messages for common API issues
- Added stream parameter support for potential future streaming capabilities

### v1.1.0
- Enhanced API error handling with specific error messages for common issues
- Improved documentation and examples

### v1.0.0
- Initial release with core functionality
- Text-to-Image generation with qwen-image model
- Image-to-Image editing with qwen-image-edit model
- Support for international and mainland China API endpoints
- Configurable parameters for image generation and editing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.