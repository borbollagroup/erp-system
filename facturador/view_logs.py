import logging

# Setup logging to write to both console and a file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("invoice_processor.log"),  # Log to file
                        logging.StreamHandler()  # Log to console
                    ])

# Use logger throughout your function to track events
logger = logging.getLogger(__name__)
