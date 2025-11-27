"""Main dictation processing pipeline."""
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.stt import STTEngine
from modules.fillers import FillerRemover
from modules.repetition import RepetitionDetector
from modules.grammar import GrammarCorrector
from modules.formatting import AutoFormatter
from modules.tone import ToneTransformer, ToneMode
from utils.latency import LatencyTracker
from utils.logger import get_logger
from config import config

logger = get_logger(__name__)

class DictationProcessor:
    """Main processing pipeline for speech dictation."""
    
    def __init__(self):
        """Initialize all processing modules."""
        logger.info("Initializing dictation processor...")
        
        # Initialize STT engine
        try:
            self.stt_engine = STTEngine(config.VOSK_MODEL_PATH)
        except Exception as e:
            logger.error(f"Failed to initialize STT engine: {e}")
            self.stt_engine = None
        
        # Initialize processing modules
        self.filler_remover = FillerRemover()
        self.repetition_detector = RepetitionDetector()
        self.grammar_corrector = GrammarCorrector(config.GRAMMAR_MODEL_NAME)
        self.formatter = AutoFormatter()
        self.tone_transformer = ToneTransformer()
        
        logger.info("Dictation processor initialized")
    
    def process_full(
        self,
        text: str,
        tone: ToneMode = "neutral",
        track_latency: bool = True
    ) -> Dict[str, Any]:
        """
        Process text through full pipeline.
        
        Args:
            text: Raw input text
            tone: Desired tone (formal, casual, concise, neutral)
            track_latency: Whether to track processing latency
            
        Returns:
            Dictionary with processed text and metadata
        """
        tracker = LatencyTracker()
        if track_latency:
            tracker.start()
        
        original_text = text
        processed_text = text
        
        # Step 1: Remove fillers
        if track_latency:
            with tracker.stage("filler_removal"):
                processed_text = self.filler_remover.remove(processed_text)
        else:
            processed_text = self.filler_remover.remove(processed_text)
        
        # Step 2: Remove repetitions
        if track_latency:
            with tracker.stage("repetition_removal"):
                processed_text = self.repetition_detector.remove_repetitions(processed_text)
        else:
            processed_text = self.repetition_detector.remove_repetitions(processed_text)
        
        # Step 3: Grammar correction
        if track_latency:
            with tracker.stage("grammar_correction"):
                processed_text = self.grammar_corrector.correct(processed_text)
        else:
            processed_text = self.grammar_corrector.correct(processed_text)
        
        # Step 4: Auto-formatting
        if track_latency:
            with tracker.stage("formatting"):
                processed_text = self.formatter.format(processed_text)
        else:
            processed_text = self.formatter.format(processed_text)
        
        # Step 5: Tone transformation
        if track_latency:
            with tracker.stage("tone_transformation"):
                processed_text = self.tone_transformer.transform(processed_text, tone)
        else:
            processed_text = self.tone_transformer.transform(processed_text, tone)
        
        if track_latency:
            tracker.end()
        
        result = {
            "original_text": original_text,
            "processed_text": processed_text,
            "tone": tone,
            "improvement": {
                "original_length": len(original_text),
                "processed_length": len(processed_text),
                "reduction_percent": (
                    (len(original_text) - len(processed_text)) / len(original_text) * 100
                    if original_text else 0
                )
            }
        }
        
        if track_latency:
            result["latency"] = tracker.get_summary()
        
        logger.info(f"Processed text: {len(original_text)} -> {len(processed_text)} chars")
        return result
    
    def process_step(
        self,
        text: str,
        step: str,
        **kwargs
    ) -> str:
        """
        Process text through a single step.
        
        Args:
            text: Input text
            step: Step name (fillers, repetition, grammar, formatting, tone)
            **kwargs: Additional arguments for specific steps
            
        Returns:
            Processed text
        """
        if step == "fillers":
            return self.filler_remover.remove(text)
        elif step == "repetition":
            return self.repetition_detector.remove_repetitions(text)
        elif step == "grammar":
            return self.grammar_corrector.correct(text)
        elif step == "formatting":
            return self.formatter.format(text)
        elif step == "tone":
            tone = kwargs.get("mode", "neutral")
            return self.tone_transformer.transform(text, tone)
        else:
            raise ValueError(f"Unknown step: {step}")
    
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        if self.stt_engine is None:
            raise RuntimeError("STT engine not initialized")
        
        return self.stt_engine.transcribe_audio_file(audio_path)
    
    def transcribe_audio_bytes(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio bytes to text.
        
        Args:
            audio_bytes: Raw audio bytes
            
        Returns:
            Transcribed text
        """
        if self.stt_engine is None:
            raise RuntimeError("STT engine not initialized")
        
        return self.stt_engine.transcribe_audio_bytes(audio_bytes)

