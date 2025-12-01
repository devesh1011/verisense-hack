"""Configuration settings for the DeFi Risk Agent."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY environment variable is not set. "
        "Please create a .env file with your Google AI API key. "
        "Get your key from: https://ai.google.dev/gemini-api/docs/api-key"
    )

# Model Configuration
MODEL_CONFIG = {
    "model": "gemini-2.0-flash",  # Fast and capable model
    "temperature": 0.2,  # Low temperature for consistent analysis
}

# Risk Assessment Thresholds
RISK_THRESHOLDS = {
    "holder_concentration": {
        "low": 0.30,  # Top 10 hold < 30%
        "medium": 0.50,  # Top 10 hold 30-50%
        "high": 0.50,  # Top 10 hold > 50%
    },
    "liquidity_usd": {
        "low": 100000,  # > $100k
        "medium": 10000,  # $10k - $100k
        "high": 10000,  # < $10k
    },
    "token_age_days": {
        "low": 180,  # > 6 months
        "medium": 30,  # 1-6 months
        "high": 30,  # < 1 month
    },
}
