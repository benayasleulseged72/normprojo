#!/usr/bin/env python3
"""
BLSC Ultimate Web Browser - Complete browser with embedded web rendering
Created by: Benayas Leulseged Software Company
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
import urllib.parse
import urllib.request
import threading
import webbrowser
import subprocess
import sys

# Try to import tkinter.html for HTML rendering
try:
    from tkinter import html
    HAS_HTML = True
except ImportError:
    HAS_HTML = False

# Try to import webview but handle it properly
try:
    import webview
    HAS_WEBVIEW = True
except ImportError:
    HAS_WEBVIEW = False

class EmbeddedWebView:
    """Embedded web view that renders HTML inside tkinter"""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.current_url = ""
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the embedded web view"""
        # Create scrolled text widget for web content
        from tkinter import scrolledtext
        
        self.web_display = scrolledtext.ScrolledText(
            self.parent,
            bg='white',
            fg='black',
            font=('Arial', 11),
            wrap=tk.WORD,
            state=tk.NORMAL,
            padx=15,
            pady=15
        )
        self.web_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for styling
        self.web_display.tag_configure('title', font=('Arial', 16, 'bold'), foreground='#1a73e8')
        self.web_display.tag_configure('heading', font=('Arial', 14, 'bold'), foreground='#333')
        self.web_display.tag_configure('link', font=('Arial', 11, 'underline'), foreground='#1a73e8')
        self.web_display.tag_configure('bold', font=('Arial', 11, 'bold'))
        self.web_display.tag_configure('center', justify='center')
    
    def load_url(self, url):
        """Load and display a URL"""
        self.current_url = url
        
        # Clear current content
        self.web_display.delete(1.0, tk.END)
        
        # Show loading message
        self.web_display.insert(tk.END, f"🌐 Loading: {url}\n\n", 'center')
        self.web_display.update()
        
        # Load content in background
        threading.Thread(target=self._load_content, args=(url,), daemon=True).start()
    
    def _load_content(self, url):
        """Load web content in background thread"""
        try:
            # Create request with proper headers
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'BLSC-Browser/1.0 (Python/Tkinter)')
            req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                content_type = response.headers.get('content-type', 'text/html')
                raw_content = response.read()
                
                # Decode content
                content = ""
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        content = raw_content.decode(encoding)
                        break
                    except:
                        continue
                
                if not content:
                    content = raw_content.decode('utf-8', errors='ignore')
                
                # Parse and display content
                if 'text/html' in content_type:
                    self._display_html(content, url)
                else:
                    self._display_text(content, url)
                    
        except Exception as e:
            self._display_error(str(e), url)
    
    def _display_html(self, html_content, url):
        """Display HTML content with basic formatting"""
        # Extract title
        import re
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "Untitled"
        
        # Extract text content and links
        from html.parser import HTMLParser
        
        class SimpleHTMLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text_content = []
                self.links = []
                self.current_tag = ""
                self.in_title = False
                self.in_script = False
                self.in_style = False
                self.current_link_url = ""
                self.current_link_text = ""
                
            def handle_starttag(self, tag, attrs):
                self.current_tag = tag.lower()
                
                if tag.lower() == 'title':
                    self.in_title = True
                elif tag.lower() in ['script', 'style']:
                    self.in_script = True
                    self.in_style = True
                elif tag.lower() == 'a':
                    for attr_name, attr_value in attrs:
                        if attr_name.lower() == 'href':
                            self.current_link_url = attr_value
                            break
                elif tag.lower() in ['p', 'div', 'br']:
                    self.text_content.append('\n')
                elif tag.lower() in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    self.text_content.append('\n\n### ')
            
            def handle_endtag(self, tag):
                if tag.lower() == 'title':
                    self.in_title = False
                elif tag.lower() in ['script', 'style']:
                    self.in_script = False
                    self.in_style = False
                elif tag.lower() == 'a' and self.current_link_url:
                    if self.current_link_text.strip():
                        self.links.append((self.current_link_text.strip(), self.current_link_url))
                    self.current_link_url = ""
                    self.current_link_text = ""
                elif tag.lower() in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    self.text_content.append(' ###\n\n')
                elif tag.lower() in ['p', 'div']:
                    self.text_content.append('\n')
            
            def handle_data(self, data):
                if not (self.in_script or self.in_style):
                    cleaned_data = ' '.join(data.split())
                    if cleaned_data:
                        self.text_content.append(cleaned_data + ' ')
                        if self.current_link_url:
                            self.current_link_text += cleaned_data + ' '
            
            def get_text(self):
                text = ''.join(self.text_content)
                text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
                text = re.sub(r' +', ' ', text)
                return text.strip()
        
        # Parse HTML
        parser = SimpleHTMLParser()
        try:
            parser.feed(html_content)
        except:
            pass
        
        # Display content in main thread
        def update_display():
            self.web_display.delete(1.0, tk.END)
            
            # Title
            self.web_display.insert(tk.END, f"🌐 {title}\n", 'title')
            self.web_display.insert(tk.END, "=" * len(title) + "\n\n", 'center')
            
            # URL and info
            self.web_display.insert(tk.END, f"📍 URL: {url}\n", 'bold')
            self.web_display.insert(tk.END, f"🕒 Loaded: {datetime.now().strftime('%H:%M:%S')}\n\n", 'bold')
            
            # Content
            self.web_display.insert(tk.END, "📄 CONTENT:\n", 'heading')
            self.web_display.insert(tk.END, "─" * 50 + "\n\n")
            
            content_text = parser.get_text()
            if content_text:
                # Format content with basic styling
                lines = content_text.split('\n')
                for line in lines:
                    if line.strip().startswith('###') and line.strip().endswith('###'):
                        # Heading
                        heading_text = line.strip().replace('###', '').strip()
                        self.web_display.insert(tk.END, f"{heading_text}\n", 'heading')
                    else:
                        self.web_display.insert(tk.END, f"{line}\n")
            else:
                self.web_display.insert(tk.END, "No readable content found.\n")
            
            # Links
            if parser.links:
                self.web_display.insert(tk.END, f"\n\n🔗 LINKS ({len(parser.links)}):\n", 'heading')
                self.web_display.insert(tk.END, "─" * 50 + "\n")
                
                for i, (link_text, link_url) in enumerate(parser.links[:15], 1):
                    self.web_display.insert(tk.END, f"{i}. {link_text[:60]}{'...' if len(link_text) > 60 else ''}\n")
                    self.web_display.insert(tk.END, f"   → {link_url}\n\n", 'link')
                
                if len(parser.links) > 15:
                    self.web_display.insert(tk.END, f"... and {len(parser.links) - 15} more links\n")
            
            # Add external browser option
            self.web_display.insert(tk.END, "\n" + "─" * 50 + "\n")
            self.web_display.insert(tk.END, "💡 For full website experience with JavaScript, CSS, and interactive features:\n", 'bold')
            self.web_display.insert(tk.END, "Click here to open in your default browser\n", 'link')
            
            # Make the "click here" text clickable
            self.web_display.tag_bind('link', '<Button-1>', lambda e: webbrowser.open(url))
            self.web_display.config(cursor='hand2')
        
        # Update display in main thread
        self.web_display.after(0, update_display)
    
    def _display_text(self, content, url):
        """Display plain text content"""
        def update_display():
            self.web_display.delete(1.0, tk.END)
            self.web_display.insert(tk.END, f"📄 {url}\n\n", 'title')
            self.web_display.insert(tk.END, content[:5000])
            if len(content) > 5000:
                self.web_display.insert(tk.END, "\n\n... (content truncated)")
        
        self.web_display.after(0, update_display)
    
    def _display_error(self, error, url):
        """Display error message"""
        def update_display():
            self.web_display.delete(1.0, tk.END)
            self.web_display.insert(tk.END, f"❌ Error loading: {url}\n\n", 'title')
            self.web_display.insert(tk.END, f"Error: {error}\n\n")
            self.web_display.insert(tk.END, "💡 Try:\n", 'bold')
            self.web_display.insert(tk.END, "• Check your internet connection\n")
            self.web_display.insert(tk.END, "• Verify the URL is correct\n")
            self.web_display.insert(tk.END, "• Click below to open in default browser\n\n")
            self.web_display.insert(tk.END, f"Open {url} in default browser", 'link')
            
            self.web_display.tag_bind('link', '<Button-1>', lambda e: webbrowser.open(url))
        
        self.web_display.after(0, update_display)

class BrowserTab:
    """Browser tab with embedded web view"""
    
    def __init__(self, parent, title="New Tab", url="https://www.google.com"):
        self.parent = parent
        self.title = title
        self.url = url
        self.frame = None
        self.web_view = None
    
    def create_tab_content(self, notebook):
        """Create tab content with embedded web view"""
        self.frame = tk.Frame(notebook, bg='white')
        self.web_view = EmbeddedWebView(self.frame)
        
        # Load the URL
        if self.url:
            self.web_view.load_url(self.url)
        
        return self.frame
    
    def navigate_to(self, url):
        """Navigate to new URL"""
        self.url = url
        if self.web_view:
            self.web_view.load_url(url)

class BLSCUltimateBrowser:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BLSC Ultimate Web Browser")
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
        """Setup browser interface"""
        # Title bar
        self.create_title_bar()
        
        # Toolbar
        self.create_toolbar()
        
        # Address bar
        self.create_address_bar()
        
        # Tab area
        self.create_tab_area()
        
        # Status bar
        self.create_status_bar()
    
    def create_title_bar(self):
        """Create title bar"""
        title_frame = tk.Frame(self.root, bg='#1e1e1e', height=35)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🌐 BLSC Ultimate Browser", 
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
        """Create toolbar"""
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
        
        # Navigation
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
        
        # Features
        bookmarks_btn = tk.Button(toolbar, text="⭐ Bookmarks", command=self.show_bookmarks, **btn_style)
        bookmarks_btn.pack(side=tk.LEFT, padx=3, pady=8)
        
        history_btn = tk.Button(toolbar, text="📚 History", command=self.show_history, **btn_style)
        history_btn.pack(side=tk.LEFT, padx=3, pady=8)
        
        # External browser
        external_btn = tk.Button(toolbar, text="🌐 External", command=self.open_external, **btn_style)
        external_btn.pack(side=tk.RIGHT, padx=(3, 15), pady=8)
    
    def create_address_bar(self):
        """Create address bar"""
        address_frame = tk.Frame(self.root, bg='#2d2d30', height=50)
        address_frame.pack(fill=tk.X, pady=2)
        address_frame.pack_propagate(False)
        
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
        
        self.status_label = tk.Label(status_frame, text="Ready - BLSC Ultimate Browser", 
                                   bg='#007acc', fg='white', font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT, padx=12, pady=3)
        
        self.tab_count_label = tk.Label(status_frame, text="Tabs: 0", 
                                      bg='#007acc', fg='white', font=('Arial', 9))
        self.tab_count_label.pack(side=tk.RIGHT, padx=12, pady=3)
    
    def new_tab(self, title="New Tab", url="https://www.google.com"):
        """Create new tab"""
        tab = BrowserTab(self, title, url)
        tab_frame = tab.create_tab_content(self.notebook)
        
        display_title = title[:15] + "..." if len(title) > 15 else title
        self.notebook.add(tab_frame, text=display_title)
        self.tabs.append(tab)
        
        # Select new tab
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
        
        self.update_status()
        self.add_to_history(url)
    
    def new_tab_dialog(self):
        """New tab dialog"""
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
    
    def close_current_tab(self):
        """Close current tab"""
        if len(self.tabs) <= 1:
            messagebox.showwarning("Cannot Close", "Cannot close the last tab!")
            return
        
        current_index = self.notebook.index(self.notebook.select())
        self.notebook.forget(current_index)
        self.tabs.pop(current_index)
        
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
                
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, self.current_tab.url)
                
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
        
        if not url.startswith(('http://', 'https://')):
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                url = f"https://www.google.com/search?q={urllib.parse.quote(url)}"
        
        if self.current_tab:
            self.current_tab.navigate_to(url)
            self.current_tab.url = url
            
            if url.startswith('https://'):
                self.security_label.config(text="🔒", fg='#4ec9b0')
            else:
                self.security_label.config(text="⚠️", fg='#f48771')
            
            self.add_to_history(url)
    
    def go_back(self):
        """Go back"""
        if len(self.history) > 1:
            self.history.pop()
            if self.history:
                prev_url = self.history[-1]
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, prev_url)
                if self.current_tab:
                    self.current_tab.navigate_to(prev_url)
    
    def go_forward(self):
        """Go forward"""
        messagebox.showinfo("Forward", "Forward navigation available in full version")
    
    def refresh(self):
        """Refresh current tab"""
        if self.current_tab:
            self.current_tab.navigate_to(self.current_tab.url)
    
    def go_home(self):
        """Go home"""
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, self.home_page)
        if self.current_tab:
            self.current_tab.navigate_to(self.home_page)
    
    def open_external(self):
        """Open current URL in external browser"""
        if self.current_tab and self.current_tab.url:
            webbrowser.open(self.current_tab.url)
    
    def add_bookmark(self):
        """Add bookmark"""
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
        """Show bookmarks"""
        if not self.bookmarks:
            messagebox.showinfo("Bookmarks", "No bookmarks saved yet!")
            return
        
        bookmarks_window = tk.Toplevel(self.root)
        bookmarks_window.title("Bookmarks")
        bookmarks_window.geometry("600x400")
        bookmarks_window.configure(bg='#2d2d30')
        
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
        """Show history"""
        if not self.history:
            messagebox.showinfo("History", "No history available!")
            return
        
        history_window = tk.Toplevel(self.root)
        history_window.title("History")
        history_window.geometry("600x400")
        history_window.configure(bg='#2d2d30')
        
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
    
    def add_to_history(self, url):
        """Add to history"""
        if url and (not self.history or self.history[-1] != url):
            self.history.append(url)
            if len(self.history) > 100:
                self.history = self.history[-100:]
    
    def update_status(self):
        """Update status"""
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
                    content = f.read().strip()
                    if content:  # Check if file is not empty
                        data = json.loads(content)
                        self.bookmarks = data.get('bookmarks', [])
                        self.history = data.get('history', [])
                        self.home_page = data.get('home_page', 'https://www.google.com')
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading data (creating new): {e}")
            # Create new empty file
            self.save_data()
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def on_closing(self):
        """Handle closing"""
        self.save_data()
        self.root.destroy()
    
    def run(self):
        """Run browser"""
        print("🌐 Starting BLSC Ultimate Browser...")
        print("📍 Created by: Benayas Leulseged Software Company")
        print("🚀 Features: Embedded web rendering, multiple tabs, bookmarks!")
        print("✨ Websites render INSIDE the browser window!")
        
        self.root.mainloop()

def main():
    """Main function"""
    browser = BLSCUltimateBrowser()
    browser.run()

if __name__ == "__main__":
    main()