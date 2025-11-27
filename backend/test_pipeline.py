"""Test script for the dictation processing pipeline."""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.processor import DictationProcessor
from modules.tone import ToneMode

def test_filler_removal():
    """Test filler removal."""
    print("Testing Filler Removal...")
    processor = DictationProcessor()
    
    test_text = "um you know I think that um the project is like really good you know"
    result = processor.process_step(test_text, "fillers")
    print(f"Original: {test_text}")
    print(f"Cleaned:  {result}\n")

def test_repetition_removal():
    """Test repetition removal."""
    print("Testing Repetition Removal...")
    processor = DictationProcessor()
    
    test_text = "The project is good. The project is good. We need to finish the project."
    result = processor.process_step(test_text, "repetition")
    print(f"Original: {test_text}")
    print(f"Cleaned:  {result}\n")

def test_grammar_correction():
    """Test grammar correction."""
    print("Testing Grammar Correction...")
    processor = DictationProcessor()
    
    test_text = "i went to the store and buyed some milk. it was good."
    result = processor.process_step(test_text, "grammar")
    print(f"Original: {test_text}")
    print(f"Corrected: {result}\n")

def test_formatting():
    """Test auto-formatting."""
    print("Testing Auto-Formatting...")
    processor = DictationProcessor()
    
    test_text = "this is a test. it needs formatting. can you help?"
    result = processor.process_step(test_text, "formatting")
    print(f"Original: {test_text}")
    print(f"Formatted: {result}\n")

def test_tone_transformation():
    """Test tone transformation."""
    print("Testing Tone Transformation...")
    processor = DictationProcessor()
    
    test_text = "I can't do that. I won't be able to help you."
    
    for tone in ["formal", "casual", "concise", "neutral"]:
        result = processor.process_step(test_text, "tone", mode=tone)
        print(f"{tone.capitalize()}: {result}")
    print()

def test_full_pipeline():
    """Test full processing pipeline."""
    print("Testing Full Pipeline...")
    processor = DictationProcessor()
    
    test_text = "um you know I think that um the project is like really good you know. The project is good. The project is good. i went to the store and buyed some milk."
    
    result = processor.process_full(test_text, tone="formal", track_latency=True)
    
    print(f"Original:  {result['original_text']}")
    print(f"Processed: {result['processed_text']}")
    print(f"Tone: {result['tone']}")
    print(f"Improvement: {result['improvement']}")
    if result.get('latency'):
        print(f"Latency: {result['latency']['total_latency_ms']:.2f}ms")
        print(f"Meets target (≤1500ms): {result['latency']['meets_target']}")
        print(f"Stage breakdown: {result['latency']['stage_breakdown']}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Dictation Engine Pipeline Tests")
    print("=" * 60)
    print()
    
    try:
        test_filler_removal()
        test_repetition_removal()
        test_grammar_correction()
        test_formatting()
        test_tone_transformation()
        test_full_pipeline()
        
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

