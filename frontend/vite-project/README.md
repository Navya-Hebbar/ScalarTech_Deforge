# Intelligent Speech Dictation Engine - Frontend

A professional, modern React frontend for the Intelligent Low-Latency Speech Dictation Engine. This frontend provides a clean, user-friendly interface for real-time speech transcription with intelligent text processing.

## Features

- 🎤 **Real-time Speech Recording** - Record audio directly from the browser
- 📝 **Side-by-Side Comparison** - View raw transcript vs. processed text simultaneously
- 🎨 **Tone/Style Control** - Choose from Formal, Casual, Concise, or Neutral tones
- ⚡ **Latency Metrics** - Real-time display of processing latency with target compliance indicator
- 📊 **Statistics** - Character count and reduction metrics
- 📋 **Copy to Clipboard** - Easy copying of both raw and processed text
- 🎯 **Modern UI** - Beautiful, responsive design with smooth animations

## Prerequisites

- Node.js 16+ and npm/yarn
- Backend API server running (default: `http://localhost:8000`)

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend/vite-project
```

2. Install dependencies:
```bash
npm install
```

## Configuration

Create a `.env` file in the `frontend/vite-project` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Update the URL to match your backend server address.

## Development

Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000` (or the next available port).

## Build

Build for production:

```bash
npm run build
```

The production build will be in the `dist` directory.

## Usage

1. **Select Tone/Style**: Choose your preferred tone from the dropdown (Formal, Casual, Concise, or Neutral)

2. **Start Recording**: Click the "Start Recording" button and grant microphone permissions when prompted

3. **Stop Recording**: Click "Stop Recording" to process the audio

4. **View Results**: 
   - Left panel shows the raw transcript from STT
   - Right panel shows the processed, cleaned, and formatted text
   - Latency metric displays processing time (target: ≤1500ms)

5. **Copy Text**: Click the clipboard icon on either panel to copy the text

6. **View Statistics**: Character counts and reduction percentage are shown below the comparison

## API Endpoints

The frontend expects the following backend endpoints:

- `POST /process/full` - Full pipeline processing
  - Body: `FormData` with `audio` file and `tone` parameter, OR JSON with `text` and `tone`
  - Response: `{ raw_transcript, processed_text, latency? }`

## Features in Detail

### Side-by-Side Comparison
- **Raw Transcript Panel**: Shows unprocessed STT output with red accent
- **Processed Text Panel**: Shows cleaned, formatted, tone-adjusted text with green accent
- Visual arrow indicator showing the transformation flow

### Latency Display
- Real-time latency measurement
- Color-coded indicator (green for ≤1500ms, yellow for >1500ms)
- Success badge when within target

### Tone Control
- **Neutral**: Standard, balanced tone
- **Formal**: Professional, business-appropriate language
- **Casual**: Conversational, relaxed tone
- **Concise**: Brief, to-the-point formatting

### Responsive Design
- Fully responsive layout with Tailwind's responsive utilities
- Mobile-friendly interface with adaptive grid layouts
- Optimized for desktop and tablet use
- Smooth animations and transitions using Tailwind's animation system

### Animations & Effects
- Fade-in animations for content loading
- Slide-up/slide-down transitions
- Scale animations on hover and click
- Pulse effects for recording state
- Gradient animations
- Smooth transform transitions
- Glassmorphism effects with backdrop blur

## Technology Stack

- **React 19** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework with custom animations
- **PostCSS** - CSS processing
- **Web APIs** - MediaRecorder API for audio capture

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari (with limitations on MediaRecorder)

## Troubleshooting

### Microphone Not Working
- Ensure browser permissions are granted
- Check that HTTPS is used (or localhost for development)
- Verify microphone is not being used by another application

### API Connection Errors
- Verify backend server is running
- Check `VITE_API_BASE_URL` in `.env` file
- Ensure CORS is properly configured on the backend

### Build Issues
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 16+)

## License

Part of the DevForge Problem Statement 4 project.
