# NavSmart  
### AI-powered Audio Navigation Proof of Concept  
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)  
[![Python version](https://img.shields.io/badge/Python-3.x-required-blue.svg)](https://www.python.org)  

## 🚀 Project Overview  
**NavSmart** is a proof-of-concept enabling audio-based navigation guided by AI.  
It processes navigation requests and returns smart voice/audio instructions suitable for mobile or web integration.  
The project aims to provide a modular, audio-first navigation experience.

## 🧩 Why this project matters  
- Enables audio-first navigation, improving accessibility.  
- API-driven approach makes it easy to integrate into various front-ends.  
- Clean separation of server logic, static assets, and UI.  
- Ideal prototype for experimenting with AI-based navigation systems.

---

## 📁 Repository Structure  

-/
-├── app/ # Core API application logic, routes, controllers
-├── static/ # Front-end assets, audio files, etc.
-├── requirements.txt # Python dependencies
-├── run.py # Main file to launch server
-├── index.html # Test UI / Landing page
-├── .gitignore
-└── README.md

---

## 🛠️ Getting Started  

### ✔ Prerequisites  
- Python 3.x  
- (Optional) Virtual environment

### ✔ Setup Instructions  
```bash
git clone https://github.com/hariom90681/nav-smart-api.git
cd nav-smart-api
pip install -r requirements.txt
```

---

## About

### Front-end / UI
- A minimal UI (index.html) is included for testing.
- Supports entering navigation inputs and listening to audio prompts.
- Extendable into a full web or mobile client.

### AI & Audio Logic
The POC demonstrates how you might integrate:
- Text-to-speech systems
- Static or generated audio cues
- uses Ollama`s llama 3.2(3B params) model keeping it lightweight
- Map-based logic or navigation SDKs
- API-based routing workflows
The project is designed to be expanded into fully dynamic voice navigation.

### Features
- Simple and clean REST API
- Modular code structure
- Audio-centric navigation output
- Scalable for use with mobile apps
- Easy UI testing via HTML frontend
