import sys
import os

# Add the root directory to Python module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask instance from app.py
from app import app

# Required for WSGI execution on Vercel
if __name__ == "__main__":
    app.run()