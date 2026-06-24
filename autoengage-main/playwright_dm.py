import sys
import argparse
import subprocess
import time
import pyperclip
from playwright.sync_api import sync_playwright

def open_linkedin_and_copy_dm(lead_url: str, message: str):
    """
    1. Copies the message to the clipboard.
    2. Opens a visible Chrome/Edge browser using Playwright.
    3. Navigates to the lead's LinkedIn URL.
    4. Keeps the browser open so the user can paste (Ctrl+V) and send manually.
    """
    
    # 1. Copy message to clipboard
    try:
        pyperclip.copy(message)
        print("✅ Message copied to clipboard. You can press Ctrl+V to paste it.")
    except Exception as e:
        print(f"⚠️ Could not copy to clipboard automatically: {e}")
        print(f"Here is the message for manual copying:\n\n{message}\n\n")

    # 2. Open Playwright visible browser
    try:
        print(f"🌐 Opening browser for {lead_url}...")
        with sync_playwright() as p:
            # Open browser in non-headless mode (visible to user)
            # We use launch_persistent_context to keep logins active if possible, 
            # but for safety/simplicity in this prototype, a standard visible launch is fine.
            # Using channel="chrome" to try and use the user's actual chrome for better chances of being logged in.
            
            try:
                 browser = p.chromium.launch_persistent_context(
                    user_data_dir="./playwright_profile", 
                    headless=False,
                    args=["--start-maximized"]
                )
            except Exception:
                # Fallback if persistent context fails
                browser = p.chromium.launch(headless=False, args=["--start-maximized"])
                browser = browser.new_context()

            page = browser.new_page()
            
            if not lead_url.startswith("http"):
                 # if it's just a username, try to guess the url
                 lead_url = f"https://www.linkedin.com/in/{lead_url}"
                 
            page.goto(lead_url)
            
            print("🚀 Browser is open. Please log in if needed, click 'Message', and press Ctrl+V.")
            print("⏳ Waiting for you to finish... (Close the browser window to end this script).")
            
            # Wait for the user to close the browser manually
            page.wait_for_event("close", timeout=0) 
            print("Browser closed.")
            
    except Exception as e:
        print(f"❌ Error opening Playwright: {e}")
        print("Fallback: opening in default system browser...")
        
        # Fallback to standard webbrowser module if playwright fails
        import webbrowser
        if not lead_url.startswith("http"):
             lead_url = f"https://www.linkedin.com/in/{lead_url}"
        webbrowser.open(lead_url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Open LinkedIn Profile and copy DM")
    parser.add_argument("--url", type=str, required=True, help="LinkedIn Profile URL or username")
    parser.add_argument("--message", type=str, required=True, help="The DM text to copy to clipboard")
    
    args = parser.parse_args()
    open_linkedin_and_copy_dm(args.url, args.message)
