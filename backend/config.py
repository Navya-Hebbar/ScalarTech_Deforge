"""Configuration management for the dictation engine."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Create necessary directories
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

class Config:
    """Application configuration."""
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Model paths
    VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", str(MODELS_DIR / "vosk-model-en-us-0.22"))
    GRAMMAR_MODEL_NAME = os.getenv("GRAMMAR_MODEL_NAME", "t5-small")
    
    # Audio settings
    MAX_AUDIO_LENGTH = int(os.getenv("MAX_AUDIO_LENGTH", "300"))
    SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "4000"))
    
    # Latency settings
    TARGET_LATENCY_MS = int(os.getenv("TARGET_LATENCY_MS", "1500"))
    PAUSE_DETECTION_MS = int(os.getenv("PAUSE_DETECTION_MS", "1000"))
    
    # Processing settings
    MAX_TEXT_LENGTH = 5000
    BATCH_SIZE = 8

config = Config()

