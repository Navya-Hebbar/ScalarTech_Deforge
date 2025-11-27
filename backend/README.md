# Intelligent Low-Latency Speech Dictation Engine - Backend

A real-time speech dictation engine that produces clean, structured, grammatically correct text with ≤1500ms latency.

## Features

- **Speech-to-Text**: Real-time transcription using Vosk
- **Filler Removal**: Eliminates disfluencies ("umm", "uhh", "you know", etc.)
- **Repetition Detection**: Removes redundant phrases
- **Grammar Correction**: Fixes sentence structure and punctuation (T5-small based)
- **Auto-Formatting**: Sentence segmentation, capitalization, punctuation
- **Tone Control**: Formal, Casual, Concise, Neutral styles
- **Low Latency**: ≤1500ms end-to-end processing

## Quick Start

### Option 1: Automated Setup
```bash
cd backend
python setup.py
```

### Option 2: Manual Setup

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Download Vosk model:**
   - Visit: https://alphacephei.com/vosk/models
   - Download: `vosk-model-en-us-0.22` (or similar)
   - Extract to: `backend/models/vosk-model-en-us-0.22`
   - Update `VOSK_MODEL_PATH` in `.env` if using a different path

3. **Download spaCy English model:**
```bash
python -m spacy download en_core_web_sm
```

4. **Set up environment:**
```bash
# Create .env file with:
# VOSK_MODEL_PATH=models/vosk-model-en-us-0.22
# GRAMMAR_MODEL_NAME=t5-small
```

5. **Run the server:**
```bash
python main.py
# OR
python run.py
```

The API will be available at `http://localhost:8000`

## Testing

Test individual components:
```bash
python test_pipeline.py
```

Test API endpoints:
```bash
# Health check
curl http://localhost:8000/health

# Full pipeline test
curl -X POST http://localhost:8000/process/full \
  -F "text=um you know I think that um the project is good" \
  -F "tone=formal"
```

## API Endpoints

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API documentation.

**Main Endpoints:**
- `GET /health` - Health check
- `POST /asr/stream` - Stream speech and get transcripts
- `POST /process/fillers` - Remove filler words
- `POST /process/repetition` - Remove repetitions
- `POST /process/grammar` - Correct grammar
- `POST /process/tone` - Transform tone/style
- `POST /process/full` - Full pipeline processing (with latency tracking)

## Architecture

```
backend/
├── main.py                    # FastAPI application
├── run.py                     # Run script
├── config.py                  # Configuration management
├── setup.py                   # Setup script
├── test_pipeline.py           # Test script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── API_DOCUMENTATION.md       # API documentation
├── utils/
│   ├── __init__.py
│   ├── latency.py             # Latency tracking
│   └── logger.py              # Logging setup
├── modules/
│   ├── stt/                   # Speech-to-Text
│   │   ├── __init__.py
│   │   └── engine.py
│   ├── fillers/               # Filler removal
│   │   ├── __init__.py
│   │   └── remover.py
│   ├── repetition/            # Repetition detection
│   │   ├── __init__.py
│   │   └── detector.py
│   ├── grammar/               # Grammar correction
│   │   ├── __init__.py
│   │   └── corrector.py
│   ├── formatting/            # Auto-formatting
│   │   ├── __init__.py
│   │   └── formatter.py
│   └── tone/                  # Tone transformation
│       ├── __init__.py
│       └── transformer.py
└── pipeline/
    ├── __init__.py
    └── processor.py           # Main processing pipeline
```

## Processing Pipeline

The full pipeline processes text in the following order:

1. **Filler Removal** - Removes "um", "uh", "you know", etc.
2. **Repetition Removal** - Detects and removes duplicate phrases
3. **Grammar Correction** - Fixes grammar using T5-small model + rules
4. **Auto-Formatting** - Adds punctuation, capitalization, paragraphing
5. **Tone Transformation** - Adjusts tone (formal/casual/concise/neutral)

## Configuration

Key configuration options in `config.py` or `.env`:

- `VOSK_MODEL_PATH`: Path to Vosk model directory
- `GRAMMAR_MODEL_NAME`: HuggingFace model name (default: "t5-small")
- `TARGET_LATENCY_MS`: Target latency in milliseconds (default: 1500)
- `SAMPLE_RATE`: Audio sample rate (default: 16000)

## Performance

- **Target Latency**: ≤1500ms for full pipeline
- **Grammar Model**: T5-small (lightweight, fast)
- **STT Engine**: Vosk (offline, low-latency)
- **Processing**: All modules run in-memory for speed

## Troubleshooting

**Issue: "Processor not initialized"**
- Check that Vosk model is downloaded and path is correct
- Verify model path in `.env` or `config.py`

**Issue: "STT engine not available"**
- Ensure Vosk model is downloaded
- Check model path configuration

**Issue: Grammar correction is slow**
- T5-small model loads on first use (may take time)
- Consider using rule-based only by setting model to None

**Issue: Import errors**
- Ensure you're running from the `backend/` directory
- Check that all dependencies are installed: `pip install -r requirements.txt`

## License

This project is part of DevForge Hackathon.
