#!/usr/bin/env python3
"""
BLSC Perfect Web Browser - Complete browser with tabs, bookmarks, and real web rendering
Created by: Benayas Leulseged Software Community
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import json
import os
from datetime import datetime
import urllib.parse
import webbrowser
import subprocess
import sys

# Try to import webview for real web rendering
try:
    import webview
    HAS_WEBVIEW = True
except ImportError:
    HAS_WEBVIEW = False
    print("WebView not available, installing...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pywebview'])
        import webview
        HAS_WEBVIEW = True
    except:
        print("Could not install webview, using embedded browser")
        HAS_WEBVIEW = False

class BrowserTab:
    """Individual browser tab"""
    def __init__(self, parent, title="New Tab", url="https://www.google.com"):
        self.parent = parent
        self.title = title
        self.url = url
        self.webview_window = None
        self.frame = None
        
    def create_tab_content(self, notebook):
        """Create the content for this tab"""
        self.frame = tk.Frame(notebook, bg='white')
        
        if HAS_WEBVIEW:
            # Create webview for real web rendering
            self.create_webview_tab()
        else:
            # Fallback to opening in default browser with info display
            self.create_fallback_tab()
        
        return self.frame
    
    def create_webview_tab(self):
        """Create webview tab with real web rendering"""
        # Info label
        info_label = tk.Label(self.frame, 
                             text=f"🌐 Loading: {self.url}\n\nThis tab opens websites in a separate window for full compatibility.",
                             bg='white', fg='#333', font=('Arial', 12), justify='center')
        info_label.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Open button
        open_btn = tk.Button(self.frame, text=f"🚀 Open {self.title}", 
                           command=self.open_in_webview,
                           bg='#0e639c', fg='white', font=('Arial', 12, 'bold'),
                           padx=20, pady=10, cursor='hand2')
        open_btn.pack(pady=10)
        
        # Auto-open the webview
        self.parent.root.after(1000, self.open_in_webview)
    
    def create_fallback_tab(self):
        """Create fallback tab that opens in default browser"""
        # Info display
        info_text = tk.Text(self.frame, bg='white', fg='#333', font=('Arial', 11),
                           wrap=tk.WORD, padx=20, pady=20)
        info_text.pack(expand=True, fill='both')
        
        content = f"""
🌐 BLSC Perfect Browser - Tab: {self.title}

📍 URL: {self.url}
🕒 Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 This website will open in your default browser for full compatibility.

💡 Features available:
• Full JavaScript support
• CSS animations and styling  
• Video and audio playback
• File downloads
• Form submissions
• All modern web features

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Click the button below to open this website:
"""
        
        info_text.insert('1.0', content)
        info_text.config(state='disabled')
        
        # Open button
        open_btn = tk.Button(self.frame, text=f"🌐 Open {self.url}", 
                           command=lambda: webbrowser.open(self.url),
                           bg='#0e639c', fg='white', font=('Arial', 12, 'bold'),
                           padx=20, pady=10, cursor='hand2')
        open_btn.pack(pady=10)
        
        # Auto-open in browser
        self.parent.root.after(2000, lambda: webbrowser.open(self.url))
    
    def open_in_webview(self):
        """Open this tab's URL in a webview window"""
        if HAS_WEBVIEW and not self.webview_window:
            try:
                self.webview_window = webview.create_window(
                    title=f"BLSC Browser - {self.title}",
                    url=self.url,
                    width=1000,
                    height=700,
                    resizable=True,
                    shadow=True
                )
                
                # Start webview in a separate thread
                def start_webview():
                    webview.start(debug=False)
                
                threading.Thread(target=start_webview, daemon=True).start()
                
            except Exception as e:
                print(f"Error opening webview: {e}")
                webbrowser.open(self.url)
        else:
            webbrowser.open(self.url)
    
    def navigate_to(self, new_url):
        """Navigate this tab to a new URL"""
        self.url = new_url
        if self.webview_window:
            try:
                self.webview_window.load_url(new_url)
            except:
                webbrowser.open(new_url)
        else:
            webbrowser.open(new_url)

class BLSCPerfectBrowser:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BLSC Perfect Web Browser")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2d2d30')
        
        # Browser data
        self.tabs = []
        self.current_tab = None
        self.history = []
        self.bookmarks = []
        self.home_page = "https://www.google.com"
        
        # Load saved data
        self.load_data()
        
        # Setup UI
        self.setup_ui()
        
        # Create first tab
        self.new_tab("Google", self.home_page)
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Setup the browser interface"""
        
        # Title bar with logo
        self.create_title_bar()
        
        # Main toolbar
        self.create_toolbar()
        
        # Address bar
        self.create_address_bar()
        
        # Tab notebook
        self.create_tab_area()
        
        # Status bar
        self.create_status_bar()
    
    def create_title_bar(self):
        """Create custom title bar"""
        title_frame = tk.Frame(self.root, bg='#1e1e1e', height=35)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        # Logo and title
        title_label = tk.Label(title_frame, text="🌐 BLSC Perfect Browser", 
                              bg='#1e1e1e', fg='white', font=('Arial', 12, 'bold'))
        title_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        # Window controls
        controls_frame = tk.Frame(title_frame, bg='#1e1e1e')
        controls_frame.pack(side=tk.RIGHT, padx=10)
        
        minimize_btn = tk.Button(controls_frame, text="−", bg='#3c3c3c', fg='white',
                               font=('Arial', 12, 'bold'), relief='flat', width=3,
                               command=self.root.iconify)
        minimize_btn.pack(side=tk.LEFT, padx=1)
        
        close_btn = tk.Button(controls_frame, text="×", bg='#e74c3c', fg='white',
                            font=('Arial', 12, 'bold'), relief='flat', width=3,
                            command=self.on_closing)
        close_btn.pack(side=tk.LEFT, padx=1)
    
    def create_toolbar(self):
        """Create main toolbar"""
        toolbar = tk.Frame(self.root, bg='#323233', height=45)
        toolbar.pack(fill=tk.X, pady=1)
        toolbar.pack_propagate(False)
        
        btn_style = {
            'bg': '#0e639c',
            'fg': 'white',
            'font': ('Arial', 10, 'bold'),
            'relief': 'flat',
            'padx': 12,
            'pady': 6,
            'cursor': 'hand2'
        }
        
        # Navigation buttons
        self.back_btn = tk.Button(toolbar, text="◀ Back", command=self.go_back, **btn_style)
        self.back_btn.pack(side=tk.LEFT, padx=(15, 3), pady=8)
        
        self.forward_btn = tk.Button(toolbar, text="Forward ▶", command=self.go_forward, **btn_style)
        self.forward_btn.pack(side=tk.LEFT, padx=3, pady=8)
        
        refresh_btn = tk.Button(toolbar, text="🔄 Refresh", command=self.refresh, **btn_style)
        refresh_btn.pack(side=tk.LEFT, padx=3, pady=8)
        
        home_btn = tk.Button(toolbar, text="🏠 Home", command=self.go_home, **btn_style)
        home_btn.pack(side=tk.LEFT, padx=3, pady=8)
        
        # Separator
        separator = tk.Frame(toolbar, width=2, bg='#555', height=30)
        separator.pack(side=tk.LEFT, padx=10, pady=8)
        
        # Tab management
        new_tab_btn = tk.Button(toolbar, text="➕ New Tab", command=self.new_tab_dialog, **btn_style)
        new_tab_btn.pack(side=tk.LEFT, padx=3, pady=8)
        
        close_tab_btn = tk.Button(toolbar, text="✖ Close Tab", command=self.close_current_tab, **btn_style)
        close_tab_btn.pack(side=tk.LEFT, padx=3, pady=8)
        
        # Separator
        separator2 = tk.Frame(toolbar, width=2, bg='#555', height=30)
        separator2.pack(side=tk.LEFT, padx=10, pady=8)
        
        # Bookmarks and history
        bookmarks_btn = tk.Button(toolbar, text="⭐ Bookmarks", command=self.show_bookmarks, **btn_style)
        bookmarks_btn.pack(side=tk.LEFT, padx=3, pady=8)
        
        history_btn = tk.Button(toolbar, text="📚 History", command=self.show_history, **btn_style)
        history_btn.pack(side=tk.LEFT, padx=3, pady=8)
        
        # Settings
        settings_btn = tk.Button(toolbar, text="⚙️ Settings", command=self.show_settings, **btn_style)
        settings_btn.pack(side=tk.RIGHT, padx=(3, 15), pady=8)
    
    def create_address_bar(self):
        """Create address bar"""
        address_frame = tk.Frame(self.root, bg='#2d2d30', height=50)
        address_frame.pack(fill=tk.X, pady=2)
        address_frame.pack_propagate(False)
        
        # URL container
        url_container = tk.Frame(address_frame, bg='#3c3c3c', relief='solid', bd=1)
        url_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Security indicator
        self.security_label = tk.Label(url_container, text="🔒", bg='#3c3c3c', 
                                     fg='#4ec9b0', font=('Arial', 12))
        self.security_label.pack(side=tk.LEFT, padx=(12, 6))
        
        # URL entry
        self.url_entry = tk.Entry(url_container, bg='#3c3c3c', fg='white', 
                                font=('Arial', 12), relief='flat', 
                                insertbackground='white')
        self.url_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=10)
        self.url_entry.bind('<Return>', self.navigate_from_entry)
        
        # Go button
        go_btn = tk.Button(url_container, text="Go", bg='#0e639c', fg='white',
                         font=('Arial', 11, 'bold'), relief='flat',
                         command=self.navigate_from_entry, cursor='hand2')
        go_btn.pack(side=tk.RIGHT, padx=(6, 12), pady=6)
        
        # Bookmark button
        bookmark_btn = tk.Button(url_container, text="⭐", bg='#3c3c3c', fg='#ffd700',
                               font=('Arial', 12), relief='flat',
                               command=self.add_bookmark, cursor='hand2')
        bookmark_btn.pack(side=tk.RIGHT, padx=3)
    
    def create_tab_area(self):
        """Create tab area"""
        # Tab notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#2d2d30', borderwidth=0)
        style.configure('TNotebook.Tab', background='#3c3c3c', foreground='white',
                       padding=[20, 8], font=('Arial', 10))
        style.map('TNotebook.Tab', background=[('selected', '#1e1e1e')])
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=(2, 5))
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, bg='#007acc', height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready - BLSC Perfect Browser", 
                                   bg='#007acc', fg='white', font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT, padx=12, pady=3)
        
        # Tab count
        self.tab_count_label = tk.Label(status_frame, text="Tabs: 0", 
                                      bg='#007acc', fg='white', font=('Arial', 9))
        self.tab_count_label.pack(side=tk.RIGHT, padx=12, pady=3)
    
    def new_tab(self, title="New Tab", url="https://www.google.com"):
        """Create a new tab"""
        tab = BrowserTab(self, title, url)
        tab_frame = tab.create_tab_content(self.notebook)
        
        self.notebook.add(tab_frame, text=title[:20] + "..." if len(title) > 20 else title)
        self.tabs.append(tab)
        
        # Select the new tab
        self.notebook.select(tab_frame)
        self.current_tab = tab
        
        # Update URL entry
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        
        # Update security indicator
        if url.startswith('https://'):
            self.security_label.config(text="🔒", fg='#4ec9b0')
        else:
            self.security_label.config(text="⚠️", fg='#f48771')
        
        # Update status
        self.update_status()
        
        # Add to history
        self.add_to_history(url)
    
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
            
            # Extract title from URL
            title = url.replace('https://', '').replace('http://', '').split('/')[0]
            self.new_tab(title, url)
    
    def close_current_tab(self):
        """Close the current tab"""
        if len(self.tabs) <= 1:
            messagebox.showwarning("Cannot Close", "Cannot close the last tab!")
            return
        
        current_index = self.notebook.index(self.notebook.select())
        
        # Remove tab
        self.notebook.forget(current_index)
        removed_tab = self.tabs.pop(current_index)
        
        # Close webview if exists
        if hasattr(removed_tab, 'webview_window') and removed_tab.webview_window:
            try:
                removed_tab.webview_window.destroy()
            except:
                pass
        
        # Select another tab
        if self.tabs:
            if current_index < len(self.tabs):
                self.current_tab = self.tabs[current_index]
            else:
                self.current_tab = self.tabs[-1]
        
        self.update_status()
    
    def on_tab_changed(self, event):
        """Handle tab change"""
        try:
            current_index = self.notebook.index(self.notebook.select())
            if 0 <= current_index < len(self.tabs):
                self.current_tab = self.tabs[current_index]
                
                # Update URL entry
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, self.current_tab.url)
                
                # Update security indicator
                if self.current_tab.url.startswith('https://'):
                    self.security_label.config(text="🔒", fg='#4ec9b0')
                else:
                    self.security_label.config(text="⚠️", fg='#f48771')
        except:
            pass
    
    def navigate_from_entry(self, event=None):
        """Navigate from URL entry"""
        url = self.url_entry.get().strip()
        if not url:
            return
        
        # Process URL
        if not url.startswith(('http://', 'https://')):
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                url = f"https://www.google.com/search?q={urllib.parse.quote(url)}"
        
        # Navigate current tab
        if self.current_tab:
            self.current_tab.navigate_to(url)
            self.current_tab.url = url
            
            # Update security indicator
            if url.startswith('https://'):
                self.security_label.config(text="🔒", fg='#4ec9b0')
            else:
                self.security_label.config(text="⚠️", fg='#f48771')
            
            # Add to history
            self.add_to_history(url)
    
    def go_back(self):
        """Go back in history"""
        if len(self.history) > 1:
            # Get previous URL
            current_url = self.history.pop()  # Remove current
            if self.history:
                prev_url = self.history[-1]
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, prev_url)
                if self.current_tab:
                    self.current_tab.navigate_to(prev_url)
    
    def go_forward(self):
        """Go forward (simplified)"""
        messagebox.showinfo("Forward", "Forward navigation would be implemented with a more complex history system")
    
    def refresh(self):
        """Refresh current tab"""
        if self.current_tab:
            self.current_tab.navigate_to(self.current_tab.url)
    
    def go_home(self):
        """Go to home page"""
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, self.home_page)
        if self.current_tab:
            self.current_tab.navigate_to(self.home_page)
    
    def add_bookmark(self):
        """Add current page to bookmarks"""
        if self.current_tab:
            title = simpledialog.askstring("Bookmark", "Enter bookmark title:",
                                         initialvalue=self.current_tab.title)
            if title:
                bookmark = {
                    "title": title,
                    "url": self.current_tab.url,
                    "date": datetime.now().isoformat()
                }
                self.bookmarks.append(bookmark)
                self.save_data()
                messagebox.showinfo("Bookmark", f"Bookmarked: {title}")
    
    def show_bookmarks(self):
        """Show bookmarks window"""
        if not self.bookmarks:
            messagebox.showinfo("Bookmarks", "No bookmarks saved yet!")
            return
        
        bookmarks_window = tk.Toplevel(self.root)
        bookmarks_window.title("Bookmarks")
        bookmarks_window.geometry("600x400")
        bookmarks_window.configure(bg='#2d2d30')
        
        # Bookmarks list
        listbox = tk.Listbox(bookmarks_window, bg='#3c3c3c', fg='white',
                           font=('Arial', 11), selectbackground='#0e639c')
        listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        for bookmark in self.bookmarks:
            listbox.insert(tk.END, f"{bookmark['title']} - {bookmark['url']}")
        
        def open_bookmark(event):
            selection = listbox.curselection()
            if selection:
                bookmark = self.bookmarks[selection[0]]
                self.new_tab(bookmark['title'], bookmark['url'])
                bookmarks_window.destroy()
        
        listbox.bind('<Double-Button-1>', open_bookmark)
    
    def show_history(self):
        """Show history window"""
        if not self.history:
            messagebox.showinfo("History", "No history available!")
            return
        
        history_window = tk.Toplevel(self.root)
        history_window.title("History")
        history_window.geometry("600x400")
        history_window.configure(bg='#2d2d30')
        
        # History list
        listbox = tk.Listbox(history_window, bg='#3c3c3c', fg='white',
                           font=('Arial', 11), selectbackground='#0e639c')
        listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        for url in reversed(self.history):
            listbox.insert(tk.END, url)
        
        def open_history_item(event):
            selection = listbox.curselection()
            if selection:
                url = self.history[-(selection[0] + 1)]
                title = url.replace('https://', '').replace('http://', '').split('/')[0]
                self.new_tab(title, url)
                history_window.destroy()
        
        listbox.bind('<Double-Button-1>', open_history_item)
    
    def show_settings(self):
        """Show settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x300")
        settings_window.configure(bg='#2d2d30')
        
        # Home page setting
        tk.Label(settings_window, text="Home Page:", bg='#2d2d30', fg='white',
                font=('Arial', 12, 'bold')).pack(pady=(20, 10))
        
        home_entry = tk.Entry(settings_window, font=('Arial', 11), width=60)
        home_entry.pack(pady=5)
        home_entry.insert(0, self.home_page)
        
        def save_settings():
            self.home_page = home_entry.get()
            self.save_data()
            messagebox.showinfo("Settings", "Settings saved!")
            settings_window.destroy()
        
        tk.Button(settings_window, text="Save Settings", command=save_settings,
                 bg='#0e639c', fg='white', font=('Arial', 11, 'bold'),
                 padx=20, pady=8).pack(pady=20)
    
    def add_to_history(self, url):
        """Add URL to history"""
        if url and (not self.history or self.history[-1] != url):
            self.history.append(url)
            if len(self.history) > 100:
                self.history = self.history[-100:]
    
    def update_status(self):
        """Update status bar"""
        tab_count = len(self.tabs)
        self.tab_count_label.config(text=f"Tabs: {tab_count}")
        
        if self.current_tab:
            self.status_label.config(text=f"Ready - {self.current_tab.title}")
    
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
                    data = json.load(f)
                    self.bookmarks = data.get('bookmarks', [])
                    self.history = data.get('history', [])
                    self.home_page = data.get('home_page', 'https://www.google.com')
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def on_closing(self):
        """Handle browser closing"""
        self.save_data()
        
        # Close all webview windows
        for tab in self.tabs:
            if hasattr(tab, 'webview_window') and tab.webview_window:
                try:
                    tab.webview_window.destroy()
                except:
                    pass
        
        self.root.destroy()
    
    def run(self):
        """Start the browser"""
        print("🌐 Starting BLSC Perfect Browser...")
        print("📍 Created by: Benayas Leulseged Software Community")
        print("🚀 Full-featured browser with tabs, bookmarks, and real web rendering!")
        print("✨ Features: Multiple tabs, bookmarks, history, settings, and more!")
        
        self.root.mainloop()

def main():
    """Main function"""
    browser = BLSCPerfectBrowser()
    browser.run()

if __name__ == "__main__":
    main()