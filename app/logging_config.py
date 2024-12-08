import logging
import os

def setup_logging():
    environment = os.getenv('FLASK_ENV', 'development')
    log_level = logging.DEBUG if environment == 'development' else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )