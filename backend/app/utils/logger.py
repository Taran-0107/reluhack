import logging
import sys
from collections import deque

# Keep the last 100 log messages in memory
log_buffer = deque(maxlen=100)

class MemoryHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_buffer.append(log_entry)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # Stdout handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Memory handler for frontend polling
        mem_handler = MemoryHandler()
        mem_handler.setLevel(logging.INFO)
        mem_handler.setFormatter(formatter)
        logger.addHandler(mem_handler)
        
    return logger

logger = setup_logger("ai-research-backend")
