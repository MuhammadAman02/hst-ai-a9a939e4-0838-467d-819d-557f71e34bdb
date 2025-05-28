import os
from dotenv import load_dotenv
from nicegui import ui

# Import the page definitions from app.main
from app.main import *  # noqa: F403, F401

# Load environment variables from .env file (if present)
load_dotenv()

if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    ui.run(
        host=host,
        port=port,
        title="Skin Tone Color Advisor",
        favicon="🎨",
        uvicorn_logging_level='info',
        reload=False
    )