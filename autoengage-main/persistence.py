"""
Persistence module for AutoEngage.
Stores and retrieves Brand Profile, Leads, DMs, Voice Samples, and Campaigns.
"""

import json
import os
from pathlib import Path

# Paths
CURRENT_DIR = Path(__file__).parent.resolve()
DATA_FILE = CURRENT_DIR / "data_store.json"

# In-memory default for brand profile
DEFAULT_BRAND = {
    "name": "TechFlow",
    "niche": "AI automation for small businesses",
    "tone": "Professional but friendly",
    "target_audience": "Small business owners, freelancers, and entrepreneurs",
    "unique_value": "We make AI simple and practical for everyday business tasks",
    "forbidden_phrases": ["buy now", "limited time", "guaranteed"],
    "cta_default": "Comment GUIDE for our free automation guide",
    "website": "https://techflow.example.com"
}

# Global in-memory lists (to keep reference integrity when imported)
BRAND = DEFAULT_BRAND.copy()
LEADS = []
CONVERSATIONS = []
VOICE_SAMPLES = []
CAMPAIGNS = []

def load_all():
    """
    Load data from JSON file into global variables.
    """
    global BRAND, LEADS, CONVERSATIONS, VOICE_SAMPLES, CAMPAIGNS
    
    if not DATA_FILE.exists():
        # Save defaults initially
        save_all()
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Load brand (merge with default keys just in case)
            BRAND.clear()
            BRAND.update(DEFAULT_BRAND)
            BRAND.update(data.get("brand", {}))
            
            # Load lists
            LEADS.clear()
            LEADS.extend(data.get("leads", []))
            
            CONVERSATIONS.clear()
            CONVERSATIONS.extend(data.get("conversations", []))
            
            VOICE_SAMPLES.clear()
            VOICE_SAMPLES.extend(data.get("voice_samples", []))
            
            CAMPAIGNS.clear()
            CAMPAIGNS.extend(data.get("campaigns", []))
            
            print(f"[Persistence] Data loaded successfully from {DATA_FILE.name}")
    except Exception as e:
        print(f"[Persistence] Error loading data: {e}. Keeping in-memory defaults.")

def save_all():
    """
    Save global variables to JSON file.
    """
    try:
        data = {
            "brand": BRAND,
            "leads": LEADS,
            "conversations": CONVERSATIONS,
            "voice_samples": VOICE_SAMPLES,
            "campaigns": CAMPAIGNS
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Persistence] Error saving data: {e}")

# Initialize load on import
load_all()
