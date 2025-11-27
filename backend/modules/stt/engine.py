"""Vosk-based Speech-to-Text engine."""
import json
import os
from pathlib import Path
from typing import Optional, Iterator
import vosk
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)

class STTEngine:
    """Speech-to-Text engine using Vosk."""
    
    def __init__(self, model_path: str):
        """
        Initialize STT engine.
        
        Args:
            model_path: Path to Vosk model directory
        """
        self.model_path = model_path
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Vosk model."""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Vosk model not found at {self.model_path}")
            
            logger.info(f"Loading Vosk model from {self.model_path}")
            self.model = vosk.Model(self.model_path)
            logger.info("Vosk model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            raise
    
    def create_recognizer(self, sample_rate: int = 16000):
        """
        Create a recognizer instance.
        
        Args:
            sample_rate: Audio sample rate
            
        Returns:
            vosk.KaldiRecognizer instance
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        return vosk.KaldiRecognizer(self.model, sample_rate)
    
    def transcribe_audio_file(self, audio_path: str, sample_rate: int = 16000) -> str:
        """
        Transcribe audio file to text with improved accuracy.
        
        Args:
            audio_path: Path to audio file
            sample_rate: Audio sample rate
            
        Returns:
            Transcribed text
        """
        import wave
        import struct
        
        try:
            wf = wave.open(audio_path, "rb")
            actual_sample_rate = wf.getframerate()
            num_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            
            # Validate and log audio format
            logger.info(f"Audio format: {num_channels} channels, {actual_sample_rate}Hz, {sample_width} bytes/sample")
            
            # Use actual sample rate
            rec = self.create_recognizer(actual_sample_rate)
            
            text_parts = []
            
            # Optimal chunk size for Vosk - balance between speed and accuracy
            # 4000 frames = ~0.25 seconds at 16kHz - good for accuracy
            chunk_size = 4000
            
            # Process audio in chunks
            try:
                while True:
                    data = wf.readframes(chunk_size)
                    if len(data) == 0:
                        break
                    
                    # Ensure we have complete frames
                    frame_size = num_channels * sample_width
                    if frame_size > 0 and len(data) % frame_size != 0:
                        # Pad to complete frame
                        padding = frame_size - (len(data) % frame_size)
                        data += b'\x00' * padding
                    
                    # Process waveform
                    if rec.AcceptWaveform(data):
                        try:
                            result = json.loads(rec.Result())
                            text = result.get("text", "").strip()
                            if text:
                                text_parts.append(text)
                                logger.debug(f"Recognized: {text}")
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.debug(f"Error parsing result: {e}")
                            continue
                
                # Get final result (important for last words)
                try:
                    final_result = json.loads(rec.FinalResult())
                    final_text = final_result.get("text", "").strip()
                    if final_text:
                        text_parts.append(final_text)
                        logger.debug(f"Final: {final_text}")
                except (json.JSONDecodeError, KeyError) as e:
                    logger.debug(f"Error parsing final result: {e}")
                
            finally:
                wf.close()
            
            # Join all parts
            transcript = " ".join(text_parts)
            if transcript:
                logger.info(f"Transcribed {len(transcript)} characters: '{transcript[:50]}...'")
            else:
                logger.info("No speech detected in audio")
            return transcript.strip()
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            raise
    
    def transcribe_audio_bytes(self, audio_bytes: bytes, sample_rate: int = 16000) -> str:
        """
        Transcribe audio bytes to text.
        
        Args:
            audio_bytes: Raw audio bytes
            sample_rate: Audio sample rate
            
        Returns:
            Transcribed text
        """
        rec = self.create_recognizer(sample_rate)
        text_parts = []
        
        # Process in chunks
        chunk_size = 4000
        for i in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[i:i + chunk_size]
            
            if rec.AcceptWaveform(chunk):
                result = json.loads(rec.Result())
                if result.get("text"):
                    text_parts.append(result["text"])
        
        # Get final result
        final_result = json.loads(rec.FinalResult())
        if final_result.get("text"):
            text_parts.append(final_result["text"])
        
        transcript = " ".join(text_parts)
        return transcript.strip()
    
    def stream_transcribe(self, audio_stream: Iterator[bytes], sample_rate: int = 16000) -> Iterator[str]:
        """
        Stream transcription from audio chunks.
        
        Args:
            audio_stream: Iterator of audio chunks
            sample_rate: Audio sample rate
            
        Yields:
            Partial transcription results
        """
        rec = self.create_recognizer(sample_rate)
        
        for chunk in audio_stream:
            if rec.AcceptWaveform(chunk):
                result = json.loads(rec.Result())
                if result.get("text"):
                    yield result["text"]
        
        # Final result
        final_result = json.loads(rec.FinalResult())
        if final_result.get("text"):
            yield final_result["text"]

