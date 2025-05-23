# VisionAID: Intelligent Assistant for the Visually Impaired 👁️‍🗨️♿

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Whisper](https://img.shields.io/badge/ASR-OpenAI_Whisper-yellow)
![OpenCV](https://img.shields.io/badge/vision-OpenCV-red)
![PyTorch](https://img.shields.io/badge/ML-PyTorch-orange)

A comprehensive assistive system featuring voice-controlled navigation, real-time object detection, barcode/product recognition, and document reading capabilities.

## Features ✨

### Navigation Module 🗺️
- Voice-controlled destination selection ("Find a hospital")
- Automatic GPS location detection
- Turn-by-turn audio guidance

### Vision Modules 👁️
| Feature | Description | Tech Used |
|---------|-------------|-----------|
| Object Detection | Identifies 80+ common objects in real-time | YOLOv5 |
| Barcode Reader | Scans EAN/UPC codes and announces products | OpenCV+ZXing |
| Product Analyzer | Reads ingredients/nutrition facts | OCR+Tesseract |
| Document Reader | Reads printed text with formatting | EasyOCR |

## Installation 💻

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/Viraj97-SL/Project1.git
cd Project1

# Install with pip
pip install -r requirements.txt

# Additional setup for audio
sudo apt-get install portaudio19-dev  # Linux
brew install portaudio               # MacOS
