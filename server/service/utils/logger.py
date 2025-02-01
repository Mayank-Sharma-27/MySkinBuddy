import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = None) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name (str): The name for the logger. If None, returns the root logger.
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    simple_formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # File Handler
    file_handler = RotatingFileHandler(
        'app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger 