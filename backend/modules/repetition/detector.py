"""Repetition detection and removal."""
import re
import sys
from pathlib import Path
from typing import List, Tuple
from collections import Counter
from Levenshtein import ratio as levenshtein_ratio

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)

class RepetitionDetector:
    """Detect and remove repeated phrases and segments."""
    
    def __init__(self, similarity_threshold: float = 0.85, min_phrase_length: int = 3):
        """
        Initialize repetition detector.
        
        Args:
            similarity_threshold: Similarity threshold for considering phrases as duplicates (0-1)
            min_phrase_length: Minimum word count for a phrase to be considered
        """
        self.similarity_threshold = similarity_threshold
        self.min_phrase_length = min_phrase_length
    
    def detect_repetitions(self, text: str) -> List[Tuple[str, int]]:
        """
        Detect repeated phrases in text.
        
        Args:
            text: Input text
            
        Returns:
            List of (phrase, count) tuples for repeated phrases
        """
        # Normalize text
        normalized = re.sub(r'[^\w\s]', ' ', text.lower())
        words = normalized.split()
        
        if len(words) < self.min_phrase_length * 2:
            return []
        
        # Generate n-grams of different sizes
        phrase_counts = Counter()
        
        # Check n-grams from min_phrase_length to half the text length
        max_ngram = min(len(words) // 2, 10)  # Cap at 10 words
        
        for n in range(self.min_phrase_length, max_ngram + 1):
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i + n])
                phrase_counts[phrase] += 1
        
        # Find phrases that appear multiple times
        repetitions = [
            (phrase, count)
            for phrase, count in phrase_counts.items()
            if count > 1
        ]
        
        # Sort by frequency and length
        repetitions.sort(key=lambda x: (x[1], len(x[0])), reverse=True)
        
        return repetitions
    
    def remove_repetitions(self, text: str) -> str:
        """
        Remove repeated phrases from text.
        
        Args:
            text: Input text with potential repetitions
            
        Returns:
            Text with repetitions removed
        """
        if not text or not text.strip():
            return text
        
        # Detect repetitions
        repetitions = self.detect_repetitions(text)
        
        if not repetitions:
            return text
        
        # Start with original text
        cleaned = text
        original_length = len(cleaned)
        
        # Remove repetitions, starting with longest/most frequent
        for phrase, count in repetitions:
            if count <= 1:
                continue
            
            # Create pattern that matches the phrase (case-insensitive, word boundaries)
            pattern = r'\b' + re.escape(phrase) + r'\b'
            
            # Find all matches
            matches = list(re.finditer(pattern, cleaned, re.IGNORECASE))
            
            if len(matches) > 1:
                # Keep only the first occurrence, remove others
                # Work backwards to preserve indices
                for match in reversed(matches[1:]):
                    start, end = match.span()
                    # Remove the match and surrounding spaces
                    before = cleaned[:start].rstrip()
                    after = cleaned[end:].lstrip()
                    cleaned = before + ' ' + after if before and after else before + after
        
        # Also check for similar phrases using Levenshtein
        cleaned = self._remove_similar_phrases(cleaned)
        
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        logger.debug(f"Removed repetitions: {original_length} -> {len(cleaned)} chars")
        return cleaned
    
    def _remove_similar_phrases(self, text: str) -> str:
        """
        Remove phrases that are very similar to each other.
        
        Args:
            text: Input text
            
        Returns:
            Text with similar phrases removed
        """
        sentences = re.split(r'([.!?]+\s*)', text)
        cleaned_sentences = []
        seen_sentences = []
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip() or sentence.strip() in '.,!?;:':
                cleaned_sentences.append(sentence)
                continue
            
            # Normalize sentence
            normalized = re.sub(r'[^\w\s]', ' ', sentence.lower()).strip()
            
            # Check similarity with previously seen sentences
            is_similar = False
            for seen in seen_sentences:
                similarity = levenshtein_ratio(normalized, seen)
                if similarity >= self.similarity_threshold:
                    is_similar = True
                    break
            
            if not is_similar:
                cleaned_sentences.append(sentence)
                if len(normalized.split()) >= self.min_phrase_length:
                    seen_sentences.append(normalized)
            else:
                # Skip similar sentence
                logger.debug(f"Skipping similar sentence: {sentence[:50]}...")
        
        return ''.join(cleaned_sentences)
    
    def remove_consecutive_repetitions(self, text: str) -> str:
        """
        Remove consecutive repeated words or phrases.
        
        Args:
            text: Input text
            
        Returns:
            Text with consecutive repetitions removed
        """
        # Remove consecutive repeated words
        pattern = r'\b(\w+)(\s+\1\b)+'
        cleaned = re.sub(pattern, r'\1', text, flags=re.IGNORECASE)
        
        # Clean up spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()

