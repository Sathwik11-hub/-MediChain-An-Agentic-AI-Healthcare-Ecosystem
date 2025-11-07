"""Test configuration."""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock settings for testing
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['ENVIRONMENT'] = 'test'
