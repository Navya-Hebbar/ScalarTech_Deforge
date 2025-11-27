"""Grammar correction using T5-small model."""
import re
import sys
import warnings
from pathlib import Path
from typing import Optional

# Suppress transformers warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*torch.utils._pytree.*")

import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.logger import get_logger
from config import config

logger = get_logger(__name__)

class GrammarCorrector:
    """Grammar correction using T5-small model."""
    
    def __init__(self, model_name: str = "t5-small"):
        """
        Initialize grammar corrector.
        
        Args:
            model_name: HuggingFace model name (default: t5-small)
        """
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Load T5 model and tokenizer."""
        try:
            logger.info(f"Loading grammar model: {self.model_name}")
            self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"Grammar model loaded on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load grammar model: {e}")
            # Fallback to rule-based correction
            logger.warning("Falling back to rule-based grammar correction")
            self.model = None
            self.tokenizer = None
    
    def correct(self, text: str) -> str:
        """
        Correct grammar in text.
        
        Args:
            text: Input text with potential grammar errors
            
        Returns:
            Grammar-corrected text
        """
        if not text or not text.strip():
            return text
        
        # First apply rule-based corrections
        corrected = self._rule_based_corrections(text)
        
        # Then apply model-based corrections if available
        if self.model and self.tokenizer:
            corrected = self._model_based_corrections(corrected)
        
        return corrected
    
    def _rule_based_corrections(self, text: str) -> str:
        """
        Apply rule-based grammar corrections.
        
        Args:
            text: Input text
            
        Returns:
            Corrected text
        """
        corrected = text
        
        # Fix common issues
        # Capitalize first letter of sentences
        corrected = re.sub(r'(^|\.\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), corrected)
        
        # Fix spacing around punctuation
        corrected = re.sub(r'\s+([,.!?;:])', r'\1', corrected)
        corrected = re.sub(r'([,.!?;:])([^\s])', r'\1 \2', corrected)
        
        # Fix double spaces
        corrected = re.sub(r'\s+', ' ', corrected)
        
        # Fix common contractions
        corrections = {
            r"(\w+)'t\s": r"\1 not ",
            r"(\w+)'re\s": r"\1 are ",
            r"(\w+)'ve\s": r"\1 have ",
            r"(\w+)'ll\s": r"\1 will ",
            r"(\w+)'d\s": r"\1 would ",
        }
        
        # Fix "its" vs "it's"
        corrected = re.sub(r"\bit's\b", "it is", corrected)
        corrected = re.sub(r"\bwon't\b", "will not", corrected)
        corrected = re.sub(r"\bcan't\b", "cannot", corrected)
        
        return corrected.strip()
    
    def _model_based_corrections(self, text: str, max_length: int = 512) -> str:
        """
        Apply model-based grammar corrections.
        
        Args:
            text: Input text
            max_length: Maximum sequence length
            
        Returns:
            Corrected text
        """
        try:
            # Split into sentences for better processing
            sentences = re.split(r'([.!?]+\s*)', text)
            corrected_sentences = []
            
            for i, sentence in enumerate(sentences):
                if not sentence.strip() or sentence.strip() in '.,!?;:':
                    corrected_sentences.append(sentence)
                    continue
                
                # Prepare input
                input_text = f"grammar: {sentence.strip()}"
                inputs = self.tokenizer.encode(
                    input_text,
                    return_tensors="pt",
                    max_length=max_length,
                    truncation=True
                ).to(self.device)
                
                # Generate correction
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=max_length,
                        num_beams=2,
                        early_stopping=True,
                        do_sample=False
                    )
                
                # Decode result
                corrected = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                corrected_sentences.append(corrected)
            
            result = ''.join(corrected_sentences)
            return result.strip()
            
        except Exception as e:
            logger.error(f"Model-based correction failed: {e}")
            # Return rule-based result if model fails
            return text
    
    def correct_sentence_structure(self, text: str) -> str:
        """
        Improve sentence structure and flow.
        
        Args:
            text: Input text
            
        Returns:
            Text with improved structure
        """
        # Split into sentences
        sentences = re.split(r'([.!?]+\s*)', text)
        improved = []
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                improved.append(sentence)
                continue
            
            # Remove sentence fragments that are too short
            words = sentence.split()
            if len(words) < 3 and i < len(sentences) - 1:
                # Merge with next sentence if too short
                continue
            
            improved.append(sentence)
        
        result = ''.join(improved)
        return re.sub(r'\s+', ' ', result).strip()

