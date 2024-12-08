from app import create_app
from app.logging_config import setup_logging
from flask import render_template
from dotenv import load_dotenv
import os

environment = os.getenv("FLASK_ENV", "development")
env_file = f".env.{environment}"
load_dotenv(env_file)
setup_logging()

app = create_app()
app.secret_key = os.getenv('SECRET_KEY', 'fallback_key')

if environment == "production" and not os.getenv("SECRET_KEY"):
    raise RuntimeError("SECRET_KEY must be set in production!")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(debug=debug_mode)

