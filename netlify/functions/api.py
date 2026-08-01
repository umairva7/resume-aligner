import sys
import os
from pathlib import Path

# Add project root directory to python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from mangum import Mangum
from app.main import app

# Mangum converts FastAPI ASGI app into Netlify Serverless handler
handler = Mangum(app, lifespan="off")
