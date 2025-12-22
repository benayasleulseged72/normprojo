#!/usr/bin/env python3
"""
BLSC Real Web Browser - A full-featured web browser with real web rendering
Uses webview library for actual web rendering like Chrome/Firefox
Created by: Benayas Leulseged Software Community
"""

import threading
import json
import os
from datetime import datetime
import urllib.parse

try:
    import webview
except ImportError:
    print("Installing required packages...")
    import subprocess
    import sys
    
    # Install required packages
    packages = ['pywebview[cef]', 'cefpython3']
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        except:
            print(f"Failed to install {package}, trying alternative...")
    
    # Try importing again
    try:
        import webview
    except ImportError:
        print("Could not install webview. Falling back to simple browser...")
        # Fallback to simple browser
        exec(open('browser.py').read())
        exit()

class BLSCRealBrowser:
    def __init__(self):
        self.history = []
        self.bookmarks = []
        self.current_url = "https://www.google.com"
        self.window = None
        
        # Load saved data
        self.load_data()
    
    def create_browser_window(self):
        """Create the main browser window"""
        
        # Create the webview window
        self.window = webview.create_window(
            title='BLSC Web Browser',
            url=self.current_url,
            width=1200,
            height=800,
            min_size=(800, 600),
            resizable=True,
            fullscreen=False,
            minimized=False,
            on_top=False,
            shadow=True,
            focus=True,
            text_select=True
        )
        
        # Set up event handlers
        self.window.events.loaded += self.on_page_loaded
        
        return self.window
    
    def on_page_loaded(self):
        """Called when a page is loaded"""
        try:
            # Get current URL
            current_url = self.window.get_current_url()
            if current_url and current_url != self.current_url:
                self.current_url = current_url
                self.add_to_history(current_url)
        except:
            pass
    
    def navigate_to(self, url):
        """Navigate to a specific URL"""
        if not url:
            return
            
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                # Search query
                url = f"https://www.google.com/search?q={urllib.parse.quote(url)}"
        
        self.current_url = url
        
        if self.window:
            self.window.load_url(url)
        
        self.add_to_history(url)
    
    def add_to_history(self, url):
        """Add URL to history"""
        if url and (not self.history or self.history[-1] != url):
            self.history.append(url)
            # Keep only last 100 entries
            if len(self.history) > 100:
                self.history = self.history[-100:]
            self.save_data()
    
    def add_bookmark(self, title, url):
        """Add bookmark"""
        bookmark = {
            "title": title,
            "url": url,
            "date": datetime.now().isoformat()
        }
        self.bookmarks.append(bookmark)
        self.save_data()
    
    def save_data(self):
        """Save browser data"""
        try:
            data = {
                'bookmarks': self.bookmarks,
                'history': self.history[-50:]  # Save last 50
            }
            with open('browser_data.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Load browser data"""
        try:
            if os.path.exists('browser_data.json'):
                with open('browser_data.json', 'r') as f:
                    data = json.load(f)
                    self.bookmarks = data.get('bookmarks', [])
                    self.history = data.get('history', [])
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def run(self):
        """Start the browser"""
        print("🌐 Starting BLSC Real Web Browser...")
        print("📍 Created by: Benayas Leulseged Software Community")
        print("🚀 Loading browser with real web rendering...")
        
        # Create and start the browser
        window = self.create_browser_window()
        
        # Start the webview
        webview.start(debug=False, http_server=False)

def main():
    """Main function"""
    try:
        browser = BLSCRealBrowser()
        browser.run()
    except Exception as e:
        print(f"Error starting real browser: {e}")
        print("Falling back to simple browser...")
        
        # Fallback to the simple browser
        try:
            exec(open('browser.py').read())
        except:
            print("Could not start any browser. Please check your Python installation.")

if __name__ == "__main__":
    main()