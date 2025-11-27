"""Filler word and disfluency removal."""
import re
import sys
from pathlib import Path
from typing import List, Set

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)

class FillerRemover:
    """Remove filler words and disfluencies from text."""
    
    # Common filler words and phrases
    FILLER_WORDS: Set[str] = {
        "um", "umm", "uh", "uhh", "eh", "ehh", "ah", "ahh",
        "er", "erm", "like", "you know", "you see", "I mean",
        "well", "so", "actually", "basically", "literally",
        "matlab", "kind of", "sort of", "right", "okay", "ok",
        "hmm", "hmmm", "uhm", "uhmm"
    }
    
    # Filler phrases (longer patterns)
    FILLER_PHRASES: List[str] = [
        r"\byou know\b",
        r"\bI mean\b",
        r"\bkind of\b",
        r"\bsort of\b",
        r"\byou see\b",
        r"\bI guess\b",
        r"\bI think\b",  # Context-dependent, but often filler
        r"\bI suppose\b",
    ]
    
    def __init__(self):
        """Initialize filler remover."""
        # Compile regex patterns for efficiency
        self.filler_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.FILLER_PHRASES
        ]
        
        # Word boundary pattern for single filler words
        self.word_boundary_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(word) for word in self.FILLER_WORDS) + r')\b',
            re.IGNORECASE
        )
    
    def remove(self, text: str) -> str:
        """
        Remove filler words and disfluencies from text.
        
        Args:
            text: Input text with potential fillers
            
        Returns:
            Text with fillers removed
        """
        if not text or not text.strip():
            return text
        
        # Remove filler phrases first (longer patterns)
        cleaned = text
        for pattern in self.filler_patterns:
            cleaned = pattern.sub('', cleaned)
        
        # Remove single filler words
        cleaned = self.word_boundary_pattern.sub('', cleaned)
        
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\s+([,.!?;:])', r'\1', cleaned)  # Remove space before punctuation
        cleaned = cleaned.strip()
        
        logger.debug(f"Removed fillers: {len(text)} -> {len(cleaned)} chars")
        return cleaned
    
    def remove_with_context(self, text: str, preserve_meaning: bool = True) -> str:
        """
        Remove fillers with context awareness.
        
        Args:
            text: Input text
            preserve_meaning: Try to preserve sentence meaning
            
        Returns:
            Cleaned text
        """
        # Split into sentences for better context
        sentences = re.split(r'([.!?]+\s*)', text)
        cleaned_sentences = []
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                cleaned_sentences.append(sentence)
                continue
            
            # Remove fillers
            cleaned = self.remove(sentence)
            
            # If sentence becomes too short after cleaning, might be mostly fillers
            if preserve_meaning and len(cleaned.split()) < 2 and len(sentence.split()) > 3:
                # Keep original if cleaning removes too much
                cleaned = sentence
            
            cleaned_sentences.append(cleaned)
        
        result = ''.join(cleaned_sentences)
        return re.sub(r'\s+', ' ', result).strip()

