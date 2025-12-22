#!/usr/bin/env python3
"""
BLSC Chrome-Like Browser - Real browser with full Chrome rendering engine
Uses CEF (Chromium Embedded Framework) for perfect web compatibility
Created by: Benayas Leulseged Software Community
"""

import sys
import os
import threading
import json
from datetime import datetime
import urllib.parse
import subprocess

# Install CEF if not available
def install_cef():
    """Install CEF Python"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'cefpython3'])
        return True
    except:
        return False

# Try to import CEF
try:
    from cefpython3 import cefpython as cef
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog
    CEF_AVAILABLE = True
except ImportError:
    print("Installing Chromium Embedded Framework...")
    if install_cef():
        try:
            from cefpython3 import cefpython as cef
            import tkinter as tk
            from tkinter import ttk, messagebox, simpledialog
            CEF_AVAILABLE = True
        except:
            CEF_AVAILABLE = False
    else:
        CEF_AVAILABLE = False

if not CEF_AVAILABLE:
    print("Could not install CEF. Creating fallback browser...")
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog
    import webbrowser

class ChromeLikeBrowser:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BLSC Chrome Browser")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f1f3f4')
        
        # Browser data
        self.tabs = []
        self.current_tab = None
        self.history = []
        self.bookmarks = []
        self.home_page = "https://www.google.com"
        
        # Load data
        self.load_data()
        
        if CEF_AVAILABLE:
            self.setup_cef()
        
        self.setup_ui()
        self.create_first_tab()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_cef(self):
        """Setup CEF"""
        sys.excepthook = cef.ExceptHook
        
        settings = {
            "multi_threaded_message_loop": False,
            "auto_zooming": "system_dpi",
            "log_severity": cef.LOGSEVERITY_ERROR,
        }
        
        cef.Initialize(settings)
    
    def setup_ui(self):
        """Setup Chrome-like UI"""
        # Chrome-style header
        self.create_chrome_header()
        
        # Tab bar
        self.create_tab_bar()
        
        # Address bar
        self.create_address_bar()
        
        # Browser area
        self.create_browser_area()
        
        # Status bar
        self.create_status_bar()
    
    def create_chrome_header(self):
        """Create Chrome-style header"""
        header = tk.Frame(self.root, bg='#ffffff', height=35)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Logo and title
        logo_frame = tk.Frame(header, bg='#ffffff')
        logo_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        logo_label = tk.Label(logo_frame, text="🌐", bg='#ffffff', 
                             font=('Arial', 16), fg='#4285f4')
        logo_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(logo_frame, text="BLSC Chrome", bg='#ffffff',
                              font=('Arial', 11, 'bold'), fg='#5f6368')
        title_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Window controls (Chrome style)
        controls = tk.Frame(header, bg='#ffffff')
        controls.pack(side=tk.RIGHT, padx=5)
        
        minimize_btn = tk.Button(controls, text="−", bg='#ffffff', fg='#5f6368',
                               font=('Arial', 14), relief='flat', width=3,
                               command=self.root.iconify, cursor='hand2')
        minimize_btn.pack(side=tk.LEFT)
        
        maximize_btn = tk.Button(controls, text="□", bg='#ffffff', fg='#5f6368',
                               font=('Arial', 12), relief='flat', width=3,
                               cursor='hand2')
        maximize_btn.pack(side=tk.LEFT)
        
        close_btn = tk.Button(controls, text="×", bg='#ffffff', fg='#5f6368',
                            font=('Arial', 14), relief='flat', width=3,
                            command=self.on_closing, cursor='hand2')
        close_btn.pack(side=tk.LEFT)
    
    def create_tab_bar(self):
        """Create Chrome-style tab bar"""
        tab_frame = tk.Frame(self.root, bg='#e8eaed', height=40)
        tab_frame.pack(fill=tk.X)
        tab_frame.pack_propagate(False)
        
        # Tab container
        self.tab_container = tk.Frame(tab_frame, bg='#e8eaed')
        self.tab_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # New tab button
        new_tab_btn = tk.Button(tab_frame, text="+", bg='#e8eaed', fg='#5f6368',
                              font=('Arial', 16, 'bold'), relief='flat', width=3,
                              command=self.new_tab_dialog, cursor='hand2')
        new_tab_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Menu button
        menu_btn = tk.Button(tab_frame, text="⋮", bg='#e8eaed', fg='#5f6368',
                           font=('Arial', 16, 'bold'), relief='flat', width=3,
                           command=self.show_menu, cursor='hand2')
        menu_btn.pack(side=tk.RIGHT, padx=2, pady=5)
    
    def create_address_bar(self):
        """Create Chrome-style address bar"""
        addr_frame = tk.Frame(self.root, bg='#ffffff', height=50)
        addr_frame.pack(fill=tk.X, padx=10, pady=5)
        addr_frame.pack_propagate(False)
        
        # Navigation buttons
        nav_frame = tk.Frame(addr_frame, bg='#ffffff')
        nav_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.back_btn = tk.Button(nav_frame, text="◀", bg='#ffffff', fg='#5f6368',
                                font=('Arial', 12), relief='flat', width=3,
                                command=self.go_back, cursor='hand2')
        self.back_btn.pack(side=tk.LEFT, padx=2)
        
        self.forward_btn = tk.Button(nav_frame, text="▶", bg='#ffffff', fg='#5f6368',
                                   font=('Arial', 12), relief='flat', width=3,
                                   command=self.go_forward, cursor='hand2')
        self.forward_btn.pack(side=tk.LEFT, padx=2)
        
        refresh_btn = tk.Button(nav_frame, text="🔄", bg='#ffffff', fg='#5f6368',
                              font=('Arial', 12), relief='flat', width=3,
                              command=self.refresh, cursor='hand2')
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        home_btn = tk.Button(nav_frame, text="🏠", bg='#ffffff', fg='#5f6368',
                           font=('Arial', 12), relief='flat', width=3,
                           command=self.go_home, cursor='hand2')
        home_btn.pack(side=tk.LEFT, padx=2)
        
        # Address bar container
        addr_container = tk.Frame(addr_frame, bg='#f1f3f4', relief='solid', bd=1)
        addr_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Security indicator
        self.security_icon = tk.Label(addr_container, text="🔒", bg='#f1f3f4',
                                    fg='#34a853', font=('Arial', 12))
        self.security_icon.pack(side=tk.LEFT, padx=(10, 5))
        
        # URL entry
        self.url_entry = tk.Entry(addr_container, bg='#f1f3f4', fg='#202124',
                                font=('Arial', 12), relief='flat',
                                insertbackground='#202124')
        self.url_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=8)
        self.url_entry.bind('<Return>', self.navigate_from_entry)
        
        # Bookmark star
        self.bookmark_btn = tk.Button(addr_container, text="☆", bg='#f1f3f4',
                                    fg='#5f6368', font=('Arial', 14), relief='flat',
                                    command=self.toggle_bookmark, cursor='hand2')
        self.bookmark_btn.pack(side=tk.RIGHT, padx=(5, 10))
        
        # Profile and settings
        profile_frame = tk.Frame(addr_frame, bg='#ffffff')
        profile_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        bookmarks_btn = tk.Button(profile_frame, text="⭐", bg='#ffffff', fg='#5f6368',
                                font=('Arial', 12), relief='flat', width=3,
                                command=self.show_bookmarks, cursor='hand2')
        bookmarks_btn.pack(side=tk.LEFT, padx=2)
        
        history_btn = tk.Button(profile_frame, text="📚", bg='#ffffff', fg='#5f6368',
                              font=('Arial', 12), relief='flat', width=3,
                              command=self.show_history, cursor='hand2')
        history_btn.pack(side=tk.LEFT, padx=2)
    
    def create_browser_area(self):
        """Create browser rendering area"""
        self.browser_frame = tk.Frame(self.root, bg='#ffffff')
        self.browser_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        
        if CEF_AVAILABLE:
            self.create_cef_browser()
        else:
            self.create_fallback_browser()
    
    def create_cef_browser(self):
        """Create CEF browser with real Chrome engine"""
        # This will be created when a tab is selected
        self.current_browser = None
        
        # Create placeholder
        placeholder = tk.Label(self.browser_frame, 
                             text="🌐 BLSC Chrome Browser\n\nReal Chromium rendering engine\nFull CSS, JavaScript, and HTML5 support",
                             bg='#ffffff', fg='#5f6368', font=('Arial', 14),
                             justify='center')
        placeholder.pack(expand=True)
    
    def create_fallback_browser(self):
        """Create fallback browser"""
        fallback_frame = tk.Frame(self.browser_frame, bg='#ffffff')
        fallback_frame.pack(fill=tk.BOTH, expand=True)
        
        info_label = tk.Label(fallback_frame,
                            text="🌐 BLSC Chrome Browser\n\nChromium engine not available\nWebsites will open in your default browser",
                            bg='#ffffff', fg='#5f6368', font=('Arial', 14),
                            justify='center')
        info_label.pack(expand=True)
    
    def create_status_bar(self):
        """Create Chrome-style status bar"""
        status_frame = tk.Frame(self.root, bg='#f1f3f4', height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready", bg='#f1f3f4',
                                   fg='#5f6368', font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=3)
        
        # Zoom and tab info
        info_frame = tk.Frame(status_frame, bg='#f1f3f4')
        info_frame.pack(side=tk.RIGHT, padx=10)
        
        self.zoom_label = tk.Label(info_frame, text="100%", bg='#f1f3f4',
                                 fg='#5f6368', font=('Arial', 9))
        self.zoom_label.pack(side=tk.RIGHT, padx=5)
        
        self.tab_count_label = tk.Label(info_frame, text="Tabs: 0", bg='#f1f3f4',
                                      fg='#5f6368', font=('Arial', 9))
        self.tab_count_label.pack(side=tk.RIGHT, padx=5)
    
    def create_first_tab(self):
        """Create the first tab"""
        self.new_tab("Google", self.home_page)
    
    def new_tab(self, title="New Tab", url="https://www.google.com"):
        """Create a new tab"""
        tab_data = {
            'title': title,
            'url': url,
            'browser': None
        }
        
        self.tabs.append(tab_data)
        self.current_tab = tab_data
        
        # Create tab button
        tab_btn = tk.Button(self.tab_container, text=title[:15] + "..." if len(title) > 15 else title,
                          bg='#ffffff', fg='#202124', font=('Arial', 10),
                          relief='flat', padx=15, pady=5,
                          command=lambda: self.select_tab(tab_data), cursor='hand2')
        tab_btn.pack(side=tk.LEFT, padx=1)
        
        tab_data['button'] = tab_btn
        
        # Update UI
        self.update_address_bar(url)
        self.update_status()
        
        # Navigate to URL
        self.navigate_to_url(url)
    
    def new_tab_dialog(self):
        """Show new tab dialog"""
        url = simpledialog.askstring("New Tab", "Enter URL or search term:",
                                    initialvalue="https://")
        if url:
            if not url.startswith(('http://', 'https://')):
                if '.' in url and ' ' not in url:
                    url = 'https://' + url
                else:
                    url = f"https://www.google.com/search?q={urllib.parse.quote(url)}"
            
            title = url.replace('https://', '').replace('http://', '').split('/')[0]
            self.new_tab(title, url)
    
    def select_tab(self, tab_data):
        """Select a tab"""
        # Update button styles
        for tab in self.tabs:
            if tab == tab_data:
                tab['button'].config(bg='#ffffff', relief='solid', bd=1)
            else:
                tab['button'].config(bg='#e8eaed', relief='flat', bd=0)
        
        self.current_tab = tab_data
        self.update_address_bar(tab_data['url'])
        
        # Switch browser if CEF is available
        if CEF_AVAILABLE and tab_data['browser']:
            # Focus on this tab's browser
            pass
    
    def navigate_to_url(self, url):
        """Navigate to URL"""
        if not url:
            return
        
        self.add_to_history(url)
        
        if CEF_AVAILABLE:
            self.navigate_cef(url)
        else:
            self.navigate_fallback(url)
    
    def navigate_cef(self, url):
        """Navigate using CEF"""
        try:
            if self.current_tab and not self.current_tab['browser']:
                # Create CEF browser for this tab
                window_info = cef.WindowInfo()
                rect = [0, 0, self.browser_frame.winfo_width(), self.browser_frame.winfo_height()]
                window_info.SetAsChild(self.browser_frame.winfo_id(), rect)
                
                browser_settings = {
                    "web_security_disabled": False,
                }
                
                browser = cef.CreateBrowserSync(window_info, url=url, settings=browser_settings)
                self.current_tab['browser'] = browser
                
                # Set up handlers
                browser.SetClientHandler(LoadHandler(self))
                
                # Update frame size
                self.browser_frame.bind('<Configure>', self.on_browser_configure)
            
            elif self.current_tab and self.current_tab['browser']:
                # Navigate existing browser
                self.current_tab['browser'].LoadUrl(url)
            
            self.status_label.config(text=f"Loading {url}...")
            
        except Exception as e:
            print(f"CEF navigation error: {e}")
            self.navigate_fallback(url)
    
    def navigate_fallback(self, url):
        """Navigate using fallback (external browser)"""
        import webbrowser
        webbrowser.open(url)
        self.status_label.config(text=f"Opened {url} in default browser")
    
    def on_browser_configure(self, event):
        """Handle browser resize"""
        if CEF_AVAILABLE and self.current_tab and self.current_tab['browser']:
            try:
                self.current_tab['browser'].SetBounds(0, 0, event.width, event.height)
            except:
                pass
    
    def navigate_from_entry(self, event=None):
        """Navigate from address bar"""
        url = self.url_entry.get().strip()
        if not url:
            return
        
        # Process URL
        if not url.startswith(('http://', 'https://')):
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                url = f"https://www.google.com/search?q={urllib.parse.quote(url)}"
        
        if self.current_tab:
            self.current_tab['url'] = url
            self.navigate_to_url(url)
            self.update_address_bar(url)
    
    def go_back(self):
        """Go back"""
        if CEF_AVAILABLE and self.current_tab and self.current_tab['browser']:
            if self.current_tab['browser'].CanGoBack():
                self.current_tab['browser'].GoBack()
        else:
            # Fallback history navigation
            if len(self.history) > 1:
                self.history.pop()
                if self.history:
                    prev_url = self.history[-1]
                    self.navigate_to_url(prev_url)
    
    def go_forward(self):
        """Go forward"""
        if CEF_AVAILABLE and self.current_tab and self.current_tab['browser']:
            if self.current_tab['browser'].CanGoForward():
                self.current_tab['browser'].GoForward()
    
    def refresh(self):
        """Refresh page"""
        if CEF_AVAILABLE and self.current_tab and self.current_tab['browser']:
            self.current_tab['browser'].Reload()
        elif self.current_tab:
            self.navigate_to_url(self.current_tab['url'])
    
    def go_home(self):
        """Go to home page"""
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, self.home_page)
        if self.current_tab:
            self.current_tab['url'] = self.home_page
            self.navigate_to_url(self.home_page)
    
    def toggle_bookmark(self):
        """Toggle bookmark"""
        if self.current_tab:
            url = self.current_tab['url']
            
            # Check if already bookmarked
            is_bookmarked = any(b['url'] == url for b in self.bookmarks)
            
            if is_bookmarked:
                # Remove bookmark
                self.bookmarks = [b for b in self.bookmarks if b['url'] != url]
                self.bookmark_btn.config(text="☆", fg='#5f6368')
                messagebox.showinfo("Bookmark", "Bookmark removed!")
            else:
                # Add bookmark
                title = simpledialog.askstring("Bookmark", "Enter bookmark title:",
                                             initialvalue=self.current_tab['title'])
                if title:
                    bookmark = {
                        "title": title,
                        "url": url,
                        "date": datetime.now().isoformat()
                    }
                    self.bookmarks.append(bookmark)
                    self.bookmark_btn.config(text="★", fg='#fbbc04')
                    messagebox.showinfo("Bookmark", f"Bookmarked: {title}")
            
            self.save_data()
    
    def show_bookmarks(self):
        """Show bookmarks"""
        if not self.bookmarks:
            messagebox.showinfo("Bookmarks", "No bookmarks saved yet!")
            return
        
        bookmarks_window = tk.Toplevel(self.root)
        bookmarks_window.title("Bookmarks")
        bookmarks_window.geometry("600x400")
        bookmarks_window.configure(bg='#ffffff')
        
        # Header
        header = tk.Label(bookmarks_window, text="📚 Bookmarks", bg='#ffffff',
                         fg='#202124', font=('Arial', 16, 'bold'))
        header.pack(pady=15)
        
        # Bookmarks list
        listbox = tk.Listbox(bookmarks_window, bg='#f8f9fa', fg='#202124',
                           font=('Arial', 11), selectbackground='#4285f4',
                           selectforeground='white')
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        for bookmark in self.bookmarks:
            listbox.insert(tk.END, f"⭐ {bookmark['title']} - {bookmark['url']}")
        
        def open_bookmark(event):
            selection = listbox.curselection()
            if selection:
                bookmark = self.bookmarks[selection[0]]
                self.new_tab(bookmark['title'], bookmark['url'])
                bookmarks_window.destroy()
        
        listbox.bind('<Double-Button-1>', open_bookmark)
    
    def show_history(self):
        """Show history"""
        if not self.history:
            messagebox.showinfo("History", "No history available!")
            return
        
        history_window = tk.Toplevel(self.root)
        history_window.title("History")
        history_window.geometry("600x400")
        history_window.configure(bg='#ffffff')
        
        # Header
        header = tk.Label(history_window, text="📚 History", bg='#ffffff',
                         fg='#202124', font=('Arial', 16, 'bold'))
        header.pack(pady=15)
        
        # History list
        listbox = tk.Listbox(history_window, bg='#f8f9fa', fg='#202124',
                           font=('Arial', 11), selectbackground='#4285f4',
                           selectforeground='white')
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        for url in reversed(self.history):
            listbox.insert(tk.END, f"🌐 {url}")
        
        def open_history_item(event):
            selection = listbox.curselection()
            if selection:
                url = self.history[-(selection[0] + 1)]
                title = url.replace('https://', '').replace('http://', '').split('/')[0]
                self.new_tab(title, url)
                history_window.destroy()
        
        listbox.bind('<Double-Button-1>', open_history_item)
    
    def show_menu(self):
        """Show browser menu"""
        menu_window = tk.Toplevel(self.root)
        menu_window.title("Menu")
        menu_window.geometry("300x400")
        menu_window.configure(bg='#ffffff')
        
        # Menu items
        menu_items = [
            ("🆕 New Tab", self.new_tab_dialog),
            ("📚 History", self.show_history),
            ("⭐ Bookmarks", self.show_bookmarks),
            ("⬇️ Downloads", lambda: messagebox.showinfo("Downloads", "Downloads feature coming soon!")),
            ("⚙️ Settings", self.show_settings),
            ("ℹ️ About", self.show_about),
        ]
        
        for text, command in menu_items:
            btn = tk.Button(menu_window, text=text, bg='#ffffff', fg='#202124',
                          font=('Arial', 12), relief='flat', anchor='w',
                          command=lambda cmd=command: [cmd(), menu_window.destroy()],
                          cursor='hand2')
            btn.pack(fill=tk.X, padx=10, pady=2)
    
    def show_settings(self):
        """Show settings"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x300")
        settings_window.configure(bg='#ffffff')
        
        # Header
        header = tk.Label(settings_window, text="⚙️ Settings", bg='#ffffff',
                         fg='#202124', font=('Arial', 16, 'bold'))
        header.pack(pady=20)
        
        # Home page setting
        tk.Label(settings_window, text="Home Page:", bg='#ffffff', fg='#202124',
                font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        home_entry = tk.Entry(settings_window, font=('Arial', 11), width=60,
                             bg='#f8f9fa', fg='#202124')
        home_entry.pack(pady=5)
        home_entry.insert(0, self.home_page)
        
        def save_settings():
            self.home_page = home_entry.get()
            self.save_data()
            messagebox.showinfo("Settings", "Settings saved!")
            settings_window.destroy()
        
        save_btn = tk.Button(settings_window, text="💾 Save Settings", command=save_settings,
                           bg='#4285f4', fg='white', font=('Arial', 11, 'bold'),
                           padx=20, pady=8, cursor='hand2')
        save_btn.pack(pady=20)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """🌐 BLSC Chrome Browser

Created by: Benayas Leulseged Software Community

Features:
• Real Chromium rendering engine
• Full CSS, JavaScript, and HTML5 support
• Multiple tabs
• Bookmarks and history
• Chrome-like interface

Version: 1.0
Built with: Python + CEF (Chromium Embedded Framework)"""
        
        messagebox.showinfo("About BLSC Chrome Browser", about_text)
    
    def update_address_bar(self, url):
        """Update address bar"""
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        
        # Update security indicator
        if url.startswith('https://'):
            self.security_icon.config(text="🔒", fg='#34a853')
        else:
            self.security_icon.config(text="⚠️", fg='#ea4335')
        
        # Update bookmark button
        is_bookmarked = any(b['url'] == url for b in self.bookmarks)
        if is_bookmarked:
            self.bookmark_btn.config(text="★", fg='#fbbc04')
        else:
            self.bookmark_btn.config(text="☆", fg='#5f6368')
    
    def update_status(self):
        """Update status bar"""
        tab_count = len(self.tabs)
        self.tab_count_label.config(text=f"Tabs: {tab_count}")
    
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
                'history': self.history[-50:],
                'home_page': self.home_page
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
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        self.bookmarks = data.get('bookmarks', [])
                        self.history = data.get('history', [])
                        self.home_page = data.get('home_page', 'https://www.google.com')
        except Exception as e:
            print(f"Error loading data: {e}")
            self.save_data()
    
    def on_closing(self):
        """Handle closing"""
        self.save_data()
        
        if CEF_AVAILABLE:
            cef.Shutdown()
        
        self.root.destroy()
    
    def run(self):
        """Run the browser"""
        print("🌐 Starting BLSC Chrome Browser...")
        print("📍 Real Chromium rendering engine")
        print("🚀 Full CSS, JavaScript, and HTML5 support!")
        
        if CEF_AVAILABLE:
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
        """Page load start"""
        if frame.IsMain():
            self.browser_app.status_label.config(text="Loading...")
    
    def OnLoadEnd(self, browser, frame, http_status_code):
        """Page load end"""
        if frame.IsMain():
            url = browser.GetUrl()
            if self.browser_app.current_tab:
                self.browser_app.current_tab['url'] = url
                self.browser_app.update_address_bar(url)
                self.browser_app.add_to_history(url)
            
            self.browser_app.status_label.config(text="Done")

def main():
    """Main function"""
    if not CEF_AVAILABLE:
        print("⚠️  CEF not available. Browser will use fallback mode.")
        print("   Websites will open in your default browser.")
        print("   To get full Chrome-like experience, install: pip install cefpython3")
    
    browser = ChromeLikeBrowser()
    browser.run()

if __name__ == "__main__":
    main()