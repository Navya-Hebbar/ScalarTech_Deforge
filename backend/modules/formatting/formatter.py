"""Auto-formatting engine for text."""
import re
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)

class AutoFormatter:
    """Auto-formatting engine for sentence segmentation, capitalization, and punctuation."""
    
    def __init__(self):
        """Initialize formatter."""
        # Sentence ending patterns
        self.sentence_endings = re.compile(r'[.!?]+\s*')
        
        # Capitalization patterns
        self.capitalize_after = re.compile(r'([.!?]\s+)([a-z])')
        self.capitalize_start = re.compile(r'^([a-z])')
    
    def format(self, text: str) -> str:
        """
        Apply comprehensive formatting to text.
        
        Args:
            text: Input text
            
        Returns:
            Formatted text
        """
        if not text or not text.strip():
            return text
        
        # Apply all formatting steps
        formatted = text
        
        # 1. Sentence segmentation
        formatted = self.segment_sentences(formatted)
        
        # 2. Capitalization
        formatted = self.fix_capitalization(formatted)
        
        # 3. Punctuation
        formatted = self.fix_punctuation(formatted)
        
        # 4. Paragraphing
        formatted = self.add_paragraphs(formatted)
        
        # 5. Final cleanup
        formatted = self.cleanup_spacing(formatted)
        
        return formatted.strip()
    
    def segment_sentences(self, text: str) -> str:
        """
        Ensure proper sentence segmentation.
        
        Args:
            text: Input text
            
        Returns:
            Text with proper sentence breaks
        """
        # Ensure sentences end with punctuation
        # Add period if sentence doesn't end with punctuation
        if text and text[-1] not in '.!?':
            text = text.rstrip() + '.'
        
        # Normalize multiple punctuation marks
        text = re.sub(r'[.!?]{2,}', lambda m: m.group(0)[0], text)
        
        # Ensure space after sentence endings
        text = re.sub(r'([.!?])([^\s])', r'\1 \2', text)
        
        return text
    
    def fix_capitalization(self, text: str) -> str:
        """
        Fix capitalization in text.
        
        Args:
            text: Input text
            
        Returns:
            Text with proper capitalization
        """
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        # Capitalize after sentence endings
        text = self.capitalize_after.sub(
            lambda m: m.group(1) + m.group(2).upper(),
            text
        )
        
        # Capitalize "I" as a word
        text = re.sub(r'\bi\b', 'I', text)
        text = re.sub(r'\bI\'m\b', "I'm", text)
        text = re.sub(r'\bI\'ve\b', "I've", text)
        text = re.sub(r'\bI\'ll\b', "I'll", text)
        text = re.sub(r'\bI\'d\b', "I'd", text)
        
        return text
    
    def fix_punctuation(self, text: str) -> str:
        """
        Fix punctuation issues.
        
        Args:
            text: Input text
            
        Returns:
            Text with fixed punctuation
        """
        # Remove spaces before punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        
        # Add space after punctuation if missing
        text = re.sub(r'([,.!?;:])([^\s])', r'\1 \2', text)
        
        # Fix multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure proper comma usage (space after)
        text = re.sub(r',([^\s])', r', \1', text)
        
        return text
    
    def add_paragraphs(self, text: str, max_sentences_per_paragraph: int = 4) -> str:
        """
        Add paragraph breaks for better readability.
        
        Args:
            text: Input text
            max_sentences_per_paragraph: Maximum sentences per paragraph
            
        Returns:
            Text with paragraph breaks
        """
        # Split into sentences
        sentences = re.split(r'([.!?]+\s*)', text)
        sentence_groups = []
        current_group = []
        
        for i, part in enumerate(sentences):
            if not part.strip():
                continue
            
            # Check if this is a sentence ending
            if re.match(r'[.!?]+\s*$', part):
                if current_group:
                    current_group.append(part)
                    sentence_groups.append(''.join(current_group))
                    current_group = []
            else:
                current_group.append(part)
        
        # Add remaining group
        if current_group:
            sentence_groups.append(''.join(current_group))
        
        # Group sentences into paragraphs
        paragraphs = []
        current_paragraph = []
        sentence_count = 0
        
        for sentence in sentence_groups:
            current_paragraph.append(sentence)
            sentence_count += 1
            
            if sentence_count >= max_sentences_per_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
                sentence_count = 0
        
        # Add remaining sentences
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        # Join paragraphs with double newline
        return '\n\n'.join(paragraphs)
    
    def cleanup_spacing(self, text: str) -> str:
        """
        Clean up spacing issues.
        
        Args:
            text: Input text
            
        Returns:
            Text with cleaned spacing
        """
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove spaces at start/end of lines
        lines = text.split('\n')
        lines = [line.strip() for line in lines]
        text = '\n'.join(lines)
        
        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def format_as_bullets(self, text: str) -> str:
        """
        Convert text to bullet list format.
        
        Args:
            text: Input text
            
        Returns:
            Text formatted as bullet points
        """
        # Split into sentences
        sentences = re.split(r'([.!?]+\s*)', text)
        bullets = []
        
        for i, part in enumerate(sentences):
            if not part.strip() or part.strip() in '.,!?;:':
                continue
            
            # Check if this looks like a list item
            sentence = part.strip()
            if sentence:
                bullets.append(f"• {sentence}")
        
        return '\n'.join(bullets)

