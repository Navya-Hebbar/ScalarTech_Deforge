"""Tone and style transformation."""
import re
import sys
from pathlib import Path
from typing import Literal

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)

ToneMode = Literal["formal", "casual", "concise", "neutral"]

class ToneTransformer:
    """Transform text tone and style."""
    
    # Formal replacements
    FORMAL_REPLACEMENTS = {
        r"\bcan't\b": "cannot",
        r"\bwon't\b": "will not",
        r"\bdon't\b": "do not",
        r"\bdidn't\b": "did not",
        r"\bisn't\b": "is not",
        r"\baren't\b": "are not",
        r"\bwasn't\b": "was not",
        r"\bweren't\b": "were not",
        r"\bhasn't\b": "has not",
        r"\bhaven't\b": "have not",
        r"\bhadn't\b": "had not",
        r"\bwouldn't\b": "would not",
        r"\bcouldn't\b": "could not",
        r"\bshouldn't\b": "should not",
        r"\bmustn't\b": "must not",
        r"\bI'm\b": "I am",
        r"\bI've\b": "I have",
        r"\bI'll\b": "I will",
        r"\bI'd\b": "I would",
        r"\byou're\b": "you are",
        r"\byou've\b": "you have",
        r"\byou'll\b": "you will",
        r"\byou'd\b": "you would",
        r"\bwe're\b": "we are",
        r"\bwe've\b": "we have",
        r"\bwe'll\b": "we will",
        r"\bwe'd\b": "we would",
        r"\bthey're\b": "they are",
        r"\bthey've\b": "they have",
        r"\bthey'll\b": "they will",
        r"\bthey'd\b": "they would",
        r"\bit's\b": "it is",
        r"\bthat's\b": "that is",
        r"\bwhat's\b": "what is",
        r"\bwho's\b": "who is",
        r"\bwhere's\b": "where is",
        r"\bhere's\b": "here is",
        r"\bthere's\b": "there is",
        r"\bgot\b": "obtained",
        r"\bget\b": "obtain",
        r"\bgot to\b": "must",
        r"\bgonna\b": "going to",
        r"\bgotta\b": "got to",
        r"\bwanna\b": "want to",
        r"\bgimme\b": "give me",
        r"\blemme\b": "let me",
    }
    
    # Casual replacements (opposite of formal)
    CASUAL_REPLACEMENTS = {
        r"\bcannot\b": "can't",
        r"\bwill not\b": "won't",
        r"\bdo not\b": "don't",
        r"\bdid not\b": "didn't",
        r"\bis not\b": "isn't",
        r"\bare not\b": "aren't",
        r"\bwas not\b": "wasn't",
        r"\bwere not\b": "weren't",
        r"\bhas not\b": "hasn't",
        r"\bhave not\b": "haven't",
        r"\bhad not\b": "hadn't",
        r"\bwould not\b": "wouldn't",
        r"\bcould not\b": "couldn't",
        r"\bshould not\b": "shouldn't",
        r"\bmust not\b": "mustn't",
        r"\bI am\b": "I'm",
        r"\bI have\b": "I've",
        r"\bI will\b": "I'll",
        r"\bI would\b": "I'd",
        r"\byou are\b": "you're",
        r"\byou have\b": "you've",
        r"\byou will\b": "you'll",
        r"\byou would\b": "you'd",
        r"\bwe are\b": "we're",
        r"\bwe have\b": "we've",
        r"\bwe will\b": "we'll",
        r"\bwe would\b": "we'd",
        r"\bthey are\b": "they're",
        r"\bthey have\b": "they've",
        r"\bthey will\b": "they'll",
        r"\bthey would\b": "they'd",
        r"\bit is\b": "it's",
        r"\bthat is\b": "that's",
        r"\bwhat is\b": "what's",
        r"\bwho is\b": "who's",
        r"\bwhere is\b": "where's",
        r"\bhere is\b": "here's",
        r"\bthere is\b": "there's",
        r"\bobtained\b": "got",
        r"\bobtain\b": "get",
        r"\bmust\b": "got to",
        r"\bgoing to\b": "gonna",
        r"\bwant to\b": "wanna",
    }
    
    # Phrases to remove for concise mode
    CONCISE_REMOVALS = [
        r"\bI think\b",
        r"\bI believe\b",
        r"\bI feel\b",
        r"\bI guess\b",
        r"\bI suppose\b",
        r"\bkind of\b",
        r"\bsort of\b",
        r"\brather\b",
        r"\bquite\b",
        r"\bvery\b",
        r"\breally\b",
        r"\bactually\b",
        r"\bbasically\b",
        r"\bliterally\b",
        r"\bessentially\b",
    ]
    
    def __init__(self):
        """Initialize tone transformer."""
        # Compile regex patterns
        self.formal_patterns = {
            re.compile(pattern, re.IGNORECASE): replacement
            for pattern, replacement in self.FORMAL_REPLACEMENTS.items()
        }
        
        self.casual_patterns = {
            re.compile(pattern, re.IGNORECASE): replacement
            for pattern, replacement in self.CASUAL_REPLACEMENTS.items()
        }
        
        self.concise_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.CONCISE_REMOVALS
        ]
    
    def transform(self, text: str, mode: ToneMode = "neutral") -> str:
        """
        Transform text tone and style.
        
        Args:
            text: Input text
            mode: Tone mode (formal, casual, concise, neutral)
            
        Returns:
            Transformed text
        """
        if not text or not text.strip():
            return text
        
        if mode == "neutral":
            return text
        
        transformed = text
        
        if mode == "formal":
            transformed = self._apply_formal(transformed)
        elif mode == "casual":
            transformed = self._apply_casual(transformed)
        elif mode == "concise":
            transformed = self._apply_concise(transformed)
        
        # Clean up spacing
        transformed = re.sub(r'\s+', ' ', transformed)
        transformed = transformed.strip()
        
        logger.debug(f"Transformed text to {mode} tone")
        return transformed
    
    def _apply_formal(self, text: str) -> str:
        """Apply formal tone transformations."""
        transformed = text
        
        # Apply formal replacements
        for pattern, replacement in self.formal_patterns.items():
            transformed = pattern.sub(replacement, transformed)
        
        # Remove casual phrases
        casual_phrases = [
            r"\byou know\b",
            r"\byou see\b",
            r"\bI mean\b",
        ]
        
        for phrase in casual_phrases:
            transformed = re.sub(phrase, '', transformed, flags=re.IGNORECASE)
        
        # Use more formal vocabulary
        vocabulary_replacements = {
            r"\bstart\b": "commence",
            r"\bstop\b": "cease",
            r"\buse\b": "utilize",
            r"\bhelp\b": "assist",
            r"\btry\b": "attempt",
        }
        
        for pattern, replacement in vocabulary_replacements.items():
            transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)
        
        return transformed
    
    def _apply_casual(self, text: str) -> str:
        """Apply casual tone transformations."""
        transformed = text
        
        # Apply casual replacements
        for pattern, replacement in self.casual_patterns.items():
            transformed = pattern.sub(replacement, transformed)
        
        return transformed
    
    def _apply_concise(self, text: str) -> str:
        """Apply concise tone transformations."""
        transformed = text
        
        # Remove verbose phrases
        for pattern in self.concise_patterns:
            transformed = pattern.sub('', transformed)
        
        # Remove redundant words
        redundant_patterns = [
            r"\bvery\s+",
            r"\breally\s+",
            r"\bquite\s+",
            r"\brather\s+",
            r"\bpretty\s+",
        ]
        
        for pattern in redundant_patterns:
            transformed = re.sub(pattern, '', transformed, flags=re.IGNORECASE)
        
        # Simplify phrases
        simplifications = {
            r"\bin order to\b": "to",
            r"\bfor the purpose of\b": "for",
            r"\bdue to the fact that\b": "because",
            r"\bat this point in time\b": "now",
            r"\bin the event that\b": "if",
        }
        
        for pattern, replacement in simplifications.items():
            transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)
        
        return transformed

