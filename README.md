# VisionAID: Intelligent Assistant for the Visually Impaired 👁️‍🗨️♿

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Whisper](https://img.shields.io/badge/ASR-OpenAI_Whisper-yellow)
![OpenCV](https://img.shields.io/badge/vision-OpenCV-red)
![PyTorch](https://img.shields.io/badge/ML-PyTorch-orange)

**VisionAID** is a multi-agent assistive system designed to empower visually impaired individuals through intelligent voice-activated modules for navigation, vision analysis, and ecommerce. Built with a modular architecture, it combines OpenAI Whisper, YOLOv8, Tesseract/EasyOCR, and HuggingFace models—all coordinated by a Master Agent using a lightweight MCP (Message Control Protocol) and logs interactions in an SQLite database.

> ✅ Designed for offline use  
> ✅ Optimized for Raspberry Pi and low-power systems  
> ✅ Modular agents and scalable architecture

---

## 🔥 Key Features

### 🗺️ Navigation Module
- Voice-guided destination selection (`"Find a pharmacy"`)
- Offline geolocation and pathfinding (OSRM, Nominatim)
- Turn-by-turn voice instructions
- Location and route planning handled via dialog agents

### 👁️ Vision Modules
| Feature | Description | Technology |
|--------|-------------|------------|
| Object Detection | Real-time object recognition | YOLOv8 + OpenCV |
| Barcode Scanner | Reads and announces product details | Pyzbar + ZXing |
| Document OCR | Reads printed materials aloud | Tesseract + EasyOCR |
| Emotion Detection | Analyzes human emotions visually | HuggingFace (`FelaKuti/Emotion-detection`) |

### 🛒 Ecommerce Agent
- Voice-based product capture using Whisper
- Live search via BeautifulSoup for Amazon/eBay
- HuggingFace-based classification and routing
- Price comparison, summarization, and negotiation logic

---

## 🏗️ Architecture

The system is composed of 3 primary subsystems:  
1. **Navigation Agent** – Handles user location, destination parsing, and route generation  
2. **Vision Agent** – Handles object, barcode, emotion, and document recognition  
3. **Ecommerce Agent** – Searches online marketplaces and compares deals  

All agents communicate via the **Master Agent** using a custom **MCP** protocol, and system interactions are logged into a **SQLite** database using `mcp_logger.py`.

```mermaid
graph TD
    User[User (Voice Input)] -->|Voice| Master[Master Agent]
    Master --> Nav[Navigation Agent]
    Master --> Vis[Vision Agent]
    Master --> Eco[Ecommerce Agent]
    Master --> UI[UI Controller]

    subgraph Navigation Subsystem
        Nav --> Dialog[Dialog Agent]
        Nav --> Location[Location Agent]
        Nav --> Route[Route Planner]
        Nav --> Navigator[Navigator]
    end

    subgraph Vision Subsystem
        Vis --> Object[Object Detection]
        Vis --> Barcode[Barcode Reader]
        Vis --> OCR[Document OCR]
        Vis --> Emotion[Emotion Detection]
    end

    subgraph Ecommerce Subsystem
        Eco --> VoiceInput[Product Capture Agent]
        Eco --> Scraper[Web Search Agent]
        Eco --> Reviews[Review Analyzer]
        Eco --> Compare[Comparison Engine]
        Eco --> Negotiate[Negotiation Agent]
        Eco --> Summary[Summary Agent]
    end
```
---

## 📦 Project Structure

```text
visionAID/
├── agents/
│   ├── ecommerce_agent/
│   │   ├── ecommerce_agent.py
│   │   ├── product_capture_agent.py
│   │   ├── web_search_agent.py
│   │   ├── summary_agent.py
│   │   ├── comparison_engine.py
│   │   ├── negotiation_agent.py
│   │   └── review_analyzer.py
│   ├── navigation/
│   │   ├── dialog_agent.py
│   │   ├── location_agent.py
│   │   ├── navigation_agent.py
│   │   ├── navigator.py
│   │   └── route_planner.py
│   └── vision_agent/
│       ├── object_detection.py
│       ├── barcode_reader.py
│       ├── document_ocr.py
│       ├── emotion_detection_agent.py
│       └── mcp_bridge.py
├── core/
│   ├── master_agent.py
│   ├── utils.py
│   ├── voice_control.py
│   ├── mcp_logger.py
│   └── config.yaml
├── yolov8n.pt                  # YOLOv8 weights
├── control_ui.py               # Tkinter-based GUI
├── requirements.txt
└── memory/                     # Audio logs and scan cache
````

---

## 🧠 Key Technologies

### 🔉 Voice & Audio

* **Speech Recognition**: OpenAI Whisper
* **Text-to-Speech**: `pygame`, `gTTS`
* **Capture**: `PyAudio`, `sounddevice`

### 🧭 Navigation

* **Pathfinding**: OSRM, Geopy
* **Location Query**: Nominatim
* **Dialog Agent**: NLP + zero-shot routing via HuggingFace

### 👁️ Vision

* **Detection**: YOLOv8 (torch + OpenCV)
* **OCR**: Tesseract + EasyOCR
* **Barcode**: ZXing, Pyzbar
* **Emotion**: HuggingFace Transformers

### 📊 Ecommerce

* **Web Scraping**: BeautifulSoup, Requests
* **Negotiation/Review**: Transformer-enhanced text summarization
* **Product Capture**: Voice interface with Whisper

---

## 💾 Installation

```bash
# Clone the repository
git clone --recurse-submodules https://github.com/Viraj97-SL/VisionAId.git
cd VisionAId

# Install dependencies
pip install -r requirements.txt

# Audio Setup (Linux)
sudo apt-get install portaudio19-dev

# Audio Setup (Mac)
brew install portaudio
```

---

## 🧪 MCP Protocol & Logging

The system uses a custom inter-agent **MCP (Message Control Protocol)** for communication across agents. All task invocations and outcomes are logged in a local SQLite database using:

```bash
vision_logs.db
```

Access logs using any SQLite viewer or via Python script.

---

## 📚 Documentation

* ✅ User Guide: \[coming soon]
* ✅ API Reference: inline in each agent file
* ✅ Development Setup: Install, run, and extend using modular structure

---

## ✅ Future Enhancements

* 🧠 Integration with LangChain for multi-step agent planning
* 🌍 Full offline ecommerce dataset cache
* 🎮 Improved GUI with vision overlays and navigation HUD

---

> Created with ❤️ by Viraj | MIT License | [GitHub Repo](https://github.com/Viraj97-SL/VisionAId)


