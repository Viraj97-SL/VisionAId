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

Project Structure 🗂️

Project1/
├── VisionAID/
│   ├── navigation/        # Voice-guided navigation
│   ├── vision/            # Object/barcode detection
│   ├── audio_processing/  # Voice I/O
│   └── utils/            # Shared utilities
├── models/
│   ├── yolo/             # Pretrained object detection
│   └── ocr/              # Text recognition models
├── docs/                 # User manuals
└── tests/                # Unit tests


Usage Examples 🚀

from VisionAID import MasterController

# Initialize all modules
assistant = MasterController()

# Object detection
assistant.detect_objects()  # Speaks detected objects

# Barcode scanning
product = assistant.scan_barcode()  
# Output: "Colgate Toothpaste, Ingredients: Sorbitol, Hydrated Silica..."

# Document reading
text = assistant.read_document()
print(text)

Key Technologies 🛠️
Voice Processing: Whisper + PyAudio

Computer Vision: OpenCV + YOLOv5

OCR: Tesseract + EasyOCR

Navigation: OSRM + Geopy

Documentation 📚
User Guide

API Reference

Development Setup
