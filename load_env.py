"""
Load environment variables from .env file
Import this at the top of pipeline scripts
"""
from dotenv import load_dotenv
import os

# Load .env file from project root
load_dotenv()
