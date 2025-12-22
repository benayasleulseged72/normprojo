#!/usr/bin/env python3
"""
BLSC Chrome Browser - Full Chrome-like browser with real web rendering
Uses CEF (Chromium Embedded Framework) for perfect web compatibility
Created by: Benayas Leulseged Software Community
"""

import sys
import os
import threading
import json
from datetime import datetime
import urllib.parse

# Try to import CEF
try:
    from cefpython3 import cefpython as cef
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog
except ImportError:
    print("Installing CEF Python...")
    import subprocess
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'cefpython3'])
        from cefpython3 import cefpython as cef
        import tkinter as tk
        from tkinter import ttk, messagebox, simpledialog
    except Exception as e:
        print(f"Could not install CEF: {e}")
        print("Falling back to simple browser...")
        exec(open('browser.py').read())
        sys.exit()

class BLSCChromeBrowser:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BLSC Chrome Browser")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2d2d30')
        
        # Browser data
        self.history = []
        self.bookmarks = []
        self.current_url = "https://www.google.com"
        self.browser = None
        
        # Load saved data
        self.load_data()
        
        # Setup CEF
        self.setup_cef()
        
        # Setup UI
        self.setup_ui()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_cef(self):
        """Setup CEF browser engine"""
        sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
        
        # CEF settings
        settings = {
            "multi_threaded_message_loop": False,
            "auto_zooming": "system_dpi",
            "log_severity": cef.LOGSEVERITY_INFO,
            "log_file": "debug.log",
        }
        
        cef.Initialize(settings)
    
    def setup_ui(self):
        """Setup the browser UI"""
        
        # Top toolbar
        self.create_toolbar()
        
        # Address bar
        self.create_address_bar()
        
        # Browser frame
        self.create_browser_frame()
        
        # Status bar
        self.create_status_bar()
    
    def create_toolbar(self):
        """Create toolbar with navigation buttons"""
        toolbar = tk.Frame(self.root, bg='#323233', height=40)
        toolbar.pack(fill=tk.X, pady=(0, 2))
        toolbar.pack_propagate(False)
        
        btn_style = {
            'bg': '#0e639c',
            'fg': 'white',
            'font': ('Arial', 9, 'bold'),
            'relief': 'flat',
            'padx': 8,
            'pady': 4,
            'cursor': 'hand2'
        }
        
        # Navigation buttons
        self.back_btn = tk.Button(toolbar, text="◀", command=self.go_back, **btn_style)
        self.back_btn.pack(side=tk.LEFT, padx=(10, 2))
        
        self.forward_btn = tk.Button(toolbar, text="▶", command=self.go_forward, **btn_style)
        self.forward_btn.pack(side=tk.LEFT, padx=2)
        
        refresh_btn = tk.Button(toolbar, text="🔄", command=self.refresh, **btn_style)
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        home_btn = tk.Button(toolbar, text="🏠", command=self.go_home, **btn_style)
        home_btn.pack(side=tk.LEFT, padx=2)
        
        # Separator
        separator = tk.Frame(toolbar, width=2, bg='#555')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        # Bookmarks and history
        bookmarks_btn = tk.Button(toolbar, text="⭐", command=self.show_bookmarks, **btn_style)
        bookmarks_btn.pack(side=tk.LEFT, padx=2)
        
        history_btn = tk.Button(toolbar, text="📚", command=self.show_history, **btn_style)
        history_btn.pack(side=tk.LEFT, padx=2)
        
        # Developer tools
        devtools_btn = tk.Button(toolbar, text="🔧", command=self.show_devtools, **btn_style)
        devtools_btn.pack(side=tk.RIGHT, padx=(2, 10))
    
    def create_address_bar(self):
        """Create address bar"""
        address_frame = tk.Frame(self.root, bg='#2d2d30', height=40)
        address_frame.pack(fill=tk.X, pady=(0, 2))
        address_frame.pack_propagate(False)
        
        # URL frame
        url_frame = tk.Frame(address_frame, bg='#3c3c3c', relief='solid', bd=1)
        url_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Security indicator
        self.security_label = tk.Label(url_frame, text="🔒", bg='#3c3c3c', fg='#4ec9b0', font=('Arial', 10))
        self.security_label.pack(side=tk.LEFT, padx=(8, 4))
        
        # URL entry
        self.url_entry = tk.Entry(url_frame, bg='#3c3c3c', fg='white', font=('Arial', 11), 
                                 relief='flat', insertbackground='white')
        self.url_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=6)
        self.url_entry.bind('<Return>', self.navigate_from_entry)
        self.url_entry.insert(0, self.current_url)
        
        # Go button
        go_btn = tk.Button(url_frame, text="Go", bg='#0e639c', fg='white', 
                          font=('Arial', 9, 'bold'), relief='flat', 
                          command=self.navigate_from_entry, cursor='hand2')
        go_btn.pack(side=tk.RIGHT, padx=(4, 8), pady=4)
        
        # Bookmark button
        bookmark_btn = tk.Button(url_frame, text="⭐", bg='#3c3c3c', fg='#ffd700', 
                                font=('Arial', 10), relief='flat', 
                                command=self.add_bookmark, cursor='hand2')
        bookmark_btn.pack(side=tk.RIGHT, padx=2)
    
    def create_browser_frame(self):
        """Create the main browser frame"""
        self.browser_frame = tk.Frame(self.root, bg='white')
        self.browser_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=(0, 2))
        
        # Create CEF browser
        self.create_cef_browser()
    
    def create_cef_browser(self):
        """Create CEF browser instance"""
        window_info = cef.WindowInfo()
        rect = [0, 0, self.browser_frame.winfo_width(), self.browser_frame.winfo_height()]
        window_info.SetAsChild(self.browser_frame.winfo_id(), rect)
        
        # Browser settings
        browser_settings = {
            "web_security_disabled": True,
            "file_access_from_file_urls_allowed": True,
            "universal_access_from_file_urls_allowed": True,
        }
        
        self.browser = cef.CreateBrowserSync(
            window_info,
            url=self.current_url,
            settings=browser_settings
        )
        
        # Set up handlers
        self.browser.SetClientHandler(LoadHandler(self))
        
        # Update frame size when window resizes
        self.browser_frame.bind('<Configure>', self.on_configure)
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, bg='#007acc', height=22)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready", bg='#007acc', 
                                   fg='white', font=('Arial', 8))
        self.status_label.pack(side=tk.LEFT, padx=8, pady=2)
        
        # Zoom level
        self.zoom_label = tk.Label(status_frame, text="100%", bg='#007acc', 
                                 fg='white', font=('Arial', 8))
        self.zoom_label.pack(side=tk.RIGHT, padx=8, pady=2)
    
    def on_configure(self, event):
        """Handle window resize"""
        if self.browser:
            self.browser.SetBounds(0, 0, event.width, event.height)
    
    def navigate_to(self, url):
        """Navigate to URL"""
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
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        
        # Update security indicator
        if url.startswith('https://'):
            self.security_label.config(text="🔒", fg='#4ec9b0')
        else:
            self.security_label.config(text="⚠️", fg='#f48771')
        
        if self.browser:
            self.browser.LoadUrl(url)
        
        self.add_to_history(url)
    
    def navigate_from_entry(self, event=None):
        """Navigate from URL entry"""
        url = self.url_entry.get().strip()
        self.navigate_to(url)
    
    def go_back(self):
        """Go back"""
        if self.browser and self.browser.CanGoBack():
            self.browser.GoBack()
    
    def go_forward(self):
        """Go forward"""
        if self.browser and self.browser.CanGoForward():
            self.browser.GoForward()
    
    def refresh(self):
        """Refresh page"""
        if self.browser:
            self.browser.Reload()
    
    def go_home(self):
        """Go to home page"""
        self.navigate_to("https://www.google.com")
    
    def show_devtools(self):
        """Show developer tools"""
        if self.browser:
            self.browser.ShowDevTools()
    
    def add_bookmark(self):
        """Add bookmark"""
        if self.current_url:
            title = simpledialog.askstring("Bookmark", "Enter bookmark title:", 
                                         initialvalue=self.browser.GetUrl() if self.browser else self.current_url)
            if title:
                bookmark = {
                    "title": title,
                    "url": self.current_url,
                    "date": datetime.now().isoformat()
                }
                self.bookmarks.append(bookmark)
                self.save_data()
                messagebox.showinfo("Bookmark", f"Bookmarked: {title}")
    
    def show_bookmarks(self):
        """Show bookmarks"""
        if not self.bookmarks:
            messagebox.showinfo("Bookmarks", "No bookmarks saved yet!")
            return
            
        bookmarks_window = tk.Toplevel(self.root)
        bookmarks_window.title("Bookmarks")
        bookmarks_window.geometry("500x400")
        bookmarks_window.configure(bg='#2d2d30')
        
        listbox = tk.Listbox(bookmarks_window, bg='#3c3c3c', fg='white', 
                           font=('Arial', 10), selectbackground='#0e639c')
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for bookmark in self.bookmarks:
            listbox.insert(tk.END, f"{bookmark['title']} - {bookmark['url']}")
        
        def open_bookmark(event):
            selection = listbox.curselection()
            if selection:
                bookmark = self.bookmarks[selection[0]]
                self.navigate_to(bookmark['url'])
                bookmarks_window.destroy()
        
        listbox.bind('<Double-Button-1>', open_bookmark)
    
    def show_history(self):
        """Show history"""
        if not self.history:
            messagebox.showinfo("History", "No history available!")
            return
            
        history_window = tk.Toplevel(self.root)
        history_window.title("History")
        history_window.geometry("500x400")
        history_window.configure(bg='#2d2d30')
        
        listbox = tk.Listbox(history_window, bg='#3c3c3c', fg='white', 
                           font=('Arial', 10), selectbackground='#0e639c')
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for url in reversed(self.history):
            listbox.insert(tk.END, url)
        
        def open_history_item(event):
            selection = listbox.curselection()
            if selection:
                url = self.history[-(selection[0] + 1)]
                self.navigate_to(url)
                history_window.destroy()
        
        listbox.bind('<Double-Button-1>', open_history_item)
    
    def add_to_history(self, url):
        """Add to history"""
        if url and (not self.history or self.history[-1] != url):
            self.history.append(url)
            if len(self.history) > 100:
                self.history = self.history[-100:]
    
    def save_data(self):
        """Save browser data"""
        try:
            data = {
                'bookmarks': self.bookmarks,
                'history': self.history[-50:]
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
    
    def on_closing(self):
        """Handle window closing"""
        self.save_data()
        cef.Shutdown()
        self.root.destroy()
    
    def run(self):
        """Run the browser"""
        print("🌐 Starting BLSC Chrome Browser...")
        print("📍 Using Chromium Embedded Framework")
        print("🚀 Full web compatibility with JavaScript, CSS, HTML5")
        
        # Start CEF message loop
        def cef_loop():
            cef.MessageLoopWork()
            self.root.after(10, cef_loop)
        
        self.root.after(10, cef_loop)
        self.root.mainloop()

class LoadHandler:
    """CEF load handler"""
    
    def __init__(self, browser_app):
        self.browser_app = browser_app
    
    def OnLoadStart(self, browser, frame, transition_type):
        """Called when page starts loading"""
        if frame.IsMain():
            self.browser_app.status_label.config(text="Loading...")
    
    def OnLoadEnd(self, browser, frame, http_status_code):
        """Called when page finishes loading"""
        if frame.IsMain():
            url = browser.GetUrl()
            self.browser_app.current_url = url
            self.browser_app.url_entry.delete(0, tk.END)
            self.browser_app.url_entry.insert(0, url)
            self.browser_app.status_label.config(text="Done")
            self.browser_app.add_to_history(url)

def main():
    """Main function"""
    try:
        browser = BLSCChromeBrowser()
        browser.run()
    except Exception as e:
        print(f"Error starting Chrome browser: {e}")
        print("Falling back to simple browser...")
        try:
            exec(open('browser.py').read())
        except:
            print("Could not start any browser.")

if __name__ == "__main__":
    main()