"""FastAPI application for Intelligent Speech Dictation Engine."""
import os
import sys
import tempfile
import warnings
from pathlib import Path
from typing import Optional

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*torch.utils._pytree.*")

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pipeline.processor import DictationProcessor
from modules.tone import ToneMode
from utils.logger import get_logger
from config import config

# Initialize logger
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Intelligent Speech Dictation Engine",
    description="Real-time speech dictation with cleaning, grammar correction, and tone control",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processor (singleton)
processor: Optional[DictationProcessor] = None

@app.on_event("startup")
async def startup_event():
    """Initialize processor on startup."""
    global processor
    try:
        logger.info("Starting up dictation engine...")
        processor = DictationProcessor()
        logger.info("Dictation engine ready")
    except Exception as e:
        logger.error(f"Failed to initialize processor: {e}")
        processor = None

# Request/Response models
class TextInput(BaseModel):
    text: str = Field(..., description="Input text to process")

class ToneInput(BaseModel):
    text: str = Field(..., description="Input text")
    mode: ToneMode = Field(default="neutral", description="Tone mode: formal, casual, concise, neutral")

class ProcessResponse(BaseModel):
    original_text: str
    processed_text: str
    tone: Optional[str] = None
    improvement: Optional[dict] = None
    latency: Optional[dict] = None

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Intelligent Speech Dictation Engine API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "processor_initialized": processor is not None
    }

@app.post("/asr/stream", response_model=ProcessResponse)
async def stream_transcription(audio: UploadFile = File(...)):
    """
    Stream speech and get transcripts.
    
    Note: This is a simplified version. For true streaming,
    you would use WebSockets or Server-Sent Events.
    """
    if processor is None:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    if processor.stt_engine is None:
        raise HTTPException(status_code=503, detail="STT engine not available")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await audio.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Transcribe
            transcript = processor.transcribe_audio(tmp_path)
            
            return ProcessResponse(
                original_text=transcript,
                processed_text=transcript,
                improvement={
                    "original_length": len(transcript),
                    "processed_length": len(transcript),
                    "reduction_percent": 0
                }
            )
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/process/fillers", response_model=ProcessResponse)
async def remove_fillers(input_data: TextInput):
    """Remove filler words and disfluencies."""
    if processor is None:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        processed = processor.process_step(input_data.text, "fillers")
        
        return ProcessResponse(
            original_text=input_data.text,
            processed_text=processed,
            improvement={
                "original_length": len(input_data.text),
                "processed_length": len(processed),
                "reduction_percent": (
                    (len(input_data.text) - len(processed)) / len(input_data.text) * 100
                    if input_data.text else 0
                )
            }
        )
    except Exception as e:
        logger.error(f"Filler removal error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/process/repetition", response_model=ProcessResponse)
async def remove_repetition(input_data: TextInput):
    """Remove repeated phrases and segments."""
    if processor is None:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        processed = processor.process_step(input_data.text, "repetition")
        
        return ProcessResponse(
            original_text=input_data.text,
            processed_text=processed,
            improvement={
                "original_length": len(input_data.text),
                "processed_length": len(processed),
                "reduction_percent": (
                    (len(input_data.text) - len(processed)) / len(input_data.text) * 100
                    if input_data.text else 0
                )
            }
        )
    except Exception as e:
        logger.error(f"Repetition removal error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/process/grammar", response_model=ProcessResponse)
async def correct_grammar(input_data: TextInput):
    """Correct grammar and sentence structure."""
    if processor is None:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        processed = processor.process_step(input_data.text, "grammar")
        
        return ProcessResponse(
            original_text=input_data.text,
            processed_text=processed,
            improvement={
                "original_length": len(input_data.text),
                "processed_length": len(processed),
                "reduction_percent": 0
            }
        )
    except Exception as e:
        logger.error(f"Grammar correction error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/process/tone", response_model=ProcessResponse)
async def transform_tone(input_data: ToneInput):
    """Transform text tone and style."""
    if processor is None:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        processed = processor.process_step(
            input_data.text,
            "tone",
            mode=input_data.mode
        )
        
        return ProcessResponse(
            original_text=input_data.text,
            processed_text=processed,
            tone=input_data.mode,
            improvement={
                "original_length": len(input_data.text),
                "processed_length": len(processed),
                "reduction_percent": (
                    (len(input_data.text) - len(processed)) / len(input_data.text) * 100
                    if input_data.text else 0
                )
            }
        )
    except Exception as e:
        logger.error(f"Tone transformation error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/process/full", response_model=ProcessResponse)
async def process_full_pipeline(
    text: str = Form(...),
    tone: ToneMode = Form(default="neutral")
):
    """
    Process text through full pipeline.
    
    Returns cleaned, formatted, tone-adjusted text with latency metrics.
    """
    if processor is None:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        result = processor.process_full(text, tone=tone, track_latency=True)
        
        return ProcessResponse(
            original_text=result["original_text"],
            processed_text=result["processed_text"],
            tone=result["tone"],
            improvement=result["improvement"],
            latency=result.get("latency")
        )
    except Exception as e:
        logger.error(f"Full pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/process/full-json")
async def process_full_pipeline_json(input_data: dict):
    """
    Process text through full pipeline (JSON body).
    
    Expected body: {"text": "...", "tone": "neutral"}
    """
    if processor is None:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        text = input_data.get("text", "")
        tone = input_data.get("tone", "neutral")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        result = processor.process_full(text, tone=tone, track_latency=True)
        
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Full pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/voice/transcribe-chunk")
async def transcribe_audio_chunk(audio: UploadFile = File(...)):
    """
    Transcribe a single audio chunk for real-time updates.
    Returns partial transcription results.
    """
    if processor is None or processor.stt_engine is None:
        return JSONResponse(content={"transcription": ""})
    
    tmp_path = None
    try:
        content = await audio.read()
        
        # Skip very small chunks
        if len(content) < 1000:
            return JSONResponse(content={"transcription": ""})
        
        file_extension = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Transcribe the chunk
        transcript = processor.transcribe_audio(tmp_path)
        
        # Return transcription (empty string if no speech detected)
        return JSONResponse(content={"transcription": transcript if transcript else ""})
        
    except Exception as e:
        logger.warning(f"Chunk transcription error: {e}")
        return JSONResponse(content={"transcription": ""})
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

@app.post("/voice/record-and-process")
async def voice_record_and_process(
    audio: UploadFile = File(...),
    tone: str = Form(default="neutral")
):
    """
    Record voice, transcribe, and process through full pipeline.
    
    This endpoint:
    1. Transcribes the audio
    2. Processes through full pipeline (fillers → repetition → grammar → formatting → tone)
    3. Returns processed text with latency metrics
    """
    if processor is None:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    if processor.stt_engine is None:
        raise HTTPException(status_code=503, detail="STT engine not available")
    
    try:
        # Get file extension from uploaded file
        file_extension = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await audio.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            import time
            pipeline_start = time.perf_counter()
            
            # Step 1: Transcribe audio
            # Vosk expects WAV format (mono, 16kHz, uncompressed)
            # Frontend should convert WebM to WAV before sending
            transcription_start = time.perf_counter()
            transcript = ""
            transcription_latency = 0
            
            try:
                # Transcribe audio - this is the critical step for accuracy
                transcript = processor.transcribe_audio(tmp_path)
                transcription_latency = (time.perf_counter() - transcription_start) * 1000
                
                logger.info(f"Transcription completed in {transcription_latency:.2f}ms: '{transcript[:50]}...'")
                
                if not transcript or not transcript.strip():
                    logger.warning("No speech detected in audio")
                    transcript = ""
                    
            except Exception as transcribe_error:
                # If transcription fails, log but don't crash - return empty
                error_msg = str(transcribe_error)
                logger.error(f"Transcription failed: {error_msg}")
                
                # Only raise error for format issues, otherwise return empty
                if "RIFF" in error_msg or "does not start" in error_msg or "format" in error_msg.lower():
                    raise HTTPException(
                        status_code=400,
                        detail="Audio format error. Please try recording again with a supported browser."
                    )
                # For other errors, just log and continue with empty transcript
                transcript = ""
                transcription_latency = (time.perf_counter() - transcription_start) * 1000
            
            # Step 2: Process through full pipeline
            # Process even if transcript is empty (will return empty processed text)
            try:
                result = processor.process_full(transcript if transcript else "", tone=tone, track_latency=True)
            except Exception as process_error:
                logger.error(f"Processing pipeline error: {process_error}")
                # Return basic result even if processing fails
                result = {
                    "original_text": transcript,
                    "processed_text": transcript,
                    "tone": tone,
                    "improvement": {
                        "original_length": len(transcript),
                        "processed_length": len(transcript),
                        "reduction_percent": 0
                    },
                    "latency": {}
                }
            
            # Calculate total pipeline latency (transcription + processing)
            total_pipeline_latency = (time.perf_counter() - pipeline_start) * 1000
            
            # Add transcription info (raw STT output - unprocessed)
            result["transcription"] = transcript if transcript else ""
            result["original_text"] = transcript if transcript else ""  # For consistency
            result["source"] = "voice"
            
            # Update latency to include transcription time
            if "latency" in result:
                result["latency"]["transcription_ms"] = round(transcription_latency, 2)
                result["latency"]["total_pipeline_ms"] = round(total_pipeline_latency, 2)
                result["latency"]["total_latency_ms"] = round(total_pipeline_latency, 2)  # Alias for compatibility
                result["latency"]["meets_target"] = total_pipeline_latency <= 1500
            else:
                result["latency"] = {
                    "transcription_ms": round(transcription_latency, 2),
                    "total_pipeline_ms": round(total_pipeline_latency, 2),
                    "total_latency_ms": round(total_pipeline_latency, 2),
                    "meets_target": total_pipeline_latency <= 1500
                }
            
            # If no speech detected, still return response but with empty transcript
            if not transcript or not transcript.strip():
                result["processed_text"] = ""
                result["improvement"] = {
                    "original_length": 0,
                    "processed_length": 0,
                    "reduction_percent": 0
                }
                logger.warning("No speech detected in audio")
            
            return JSONResponse(content=result)
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

