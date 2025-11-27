# Frontend - Intelligent Speech Dictation Engine

A React-based frontend for the Intelligent Low-Latency Speech Dictation Engine.

## Features

- 📝 **Text Processing**: Process text through the full pipeline or individual steps
- 🎵 **Audio Transcription**: Upload audio files for speech-to-text
- 🎨 **Tone Control**: Choose from Formal, Casual, Concise, or Neutral
- 📊 **Results Display**: Side-by-side before/after comparison
- ⏱️ **Latency Tracking**: View processing time and stage breakdown
- 📋 **Copy to Clipboard**: Easy copy functionality

## Setup

1. **Navigate to frontend directory:**
```bash
cd frontend/vite-project
```

2. **Install dependencies (if needed):**
```bash
npm install
```

3. **Start the development server:**
```bash
npm run dev
```

4. **Open in browser:**
The app will be available at `http://localhost:5173` (or the port shown in terminal)

## Usage

### Text Processing
1. Switch to "Text Processing" tab
2. Enter or paste your text
3. Select desired tone (Formal, Casual, Concise, Neutral)
4. Click "Process Full Pipeline" for complete processing
5. Or use individual step buttons:
   - Remove Fillers
   - Remove Repetition
   - Correct Grammar
   - Transform Tone

### Audio Transcription
1. Switch to "Audio Transcription" tab
2. Upload an audio file (WAV format recommended)
3. Click "Transcribe Audio"
4. The transcribed text will appear and can be further processed

### Viewing Results
- **Before/After Comparison**: See original vs processed text side-by-side
- **Improvement Metrics**: View character reduction and statistics
- **Latency Information**: See total processing time and per-stage breakdown
- **Copy Button**: Copy processed text to clipboard

## Backend Connection

The frontend connects to the backend API at:
- **Default**: `http://localhost:8000`

To change the backend URL, edit `API_BASE_URL` in `src/App.jsx`:

```javascript
const API_BASE_URL = 'http://localhost:8000'
```

## Requirements

- Node.js (v16 or higher)
- npm or yarn
- Backend server running on port 8000

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.
