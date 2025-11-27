"""Latency tracking utilities."""
import time
from typing import Dict, Optional
from contextlib import contextmanager

class LatencyTracker:
    """Track processing latency for different pipeline stages."""
    
    def __init__(self):
        self.stages: Dict[str, float] = {}
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def start(self):
        """Start overall timing."""
        self.start_time = time.time()
        self.stages.clear()
    
    def end(self):
        """End overall timing."""
        self.end_time = time.time()
    
    @contextmanager
    def stage(self, stage_name: str):
        """Context manager for tracking stage latency."""
        stage_start = time.time()
        try:
            yield
        finally:
            stage_end = time.time()
            self.stages[stage_name] = (stage_end - stage_start) * 1000  # Convert to ms
    
    def get_total_latency_ms(self) -> float:
        """Get total latency in milliseconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0
    
    def get_stage_latencies(self) -> Dict[str, float]:
        """Get latency breakdown by stage."""
        return self.stages.copy()
    
    def get_summary(self) -> Dict:
        """Get complete latency summary."""
        return {
            "total_latency_ms": self.get_total_latency_ms(),
            "stage_breakdown": self.get_stage_latencies(),
            "meets_target": self.get_total_latency_ms() <= 1500
        }

