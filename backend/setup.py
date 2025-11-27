"""Setup script for installing dependencies and downloading models."""
import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✓ Dependencies installed")

def download_spacy_model():
    """Download spaCy English model."""
    print("Downloading spaCy English model...")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✓ spaCy model downloaded")
    except subprocess.CalledProcessError:
        print("⚠ Failed to download spaCy model. You may need to install it manually:")
        print("  python -m spacy download en_core_web_sm")

def download_vosk_model():
    """Download Vosk model."""
    print("\n⚠ Vosk model needs to be downloaded manually:")
    print("  1. Visit: https://alphacephei.com/vosk/models")
    print("  2. Download: vosk-model-en-us-0.22 (or similar)")
    print("  3. Extract to: backend/models/vosk-model-en-us-0.22")
    print("  4. Update VOSK_MODEL_PATH in .env if different")

def create_directories():
    """Create necessary directories."""
    dirs = ["models", "logs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("✓ Directories created")

def main():
    """Run setup."""
    print("Setting up Intelligent Speech Dictation Engine...\n")
    
    create_directories()
    install_dependencies()
    download_spacy_model()
    download_vosk_model()
    
    print("\n✓ Setup complete!")
    print("\nNext steps:")
    print("  1. Download Vosk model (see instructions above)")
    print("  2. Copy .env.example to .env and configure if needed")
    print("  3. Run: python main.py")

if __name__ == "__main__":
    main()

