"""
Start the Flask web application.

Usage:
  python run.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.app import run

if __name__ == "__main__":
    print("Starting CyberDetect at http://localhost:5000")
    run()
