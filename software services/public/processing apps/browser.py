#!/usr/bin/env python3
"""
BLSC Web Browser - A full-featured web browser built with Python Tkinter
Created by: Benayas Leulseged Software Community
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import urllib.request
import urllib.parse
from tkinter import scrolledtext
import threading
import json
import os
from datetime import datetime
import re
import html
from html.parser import HTMLParser

class SimpleHTMLParser(HTMLParser):
    """Simple HTML parser to extract readable content"""
    
    def __init__(self):
        super().__init__()
        self.title = ""
        self.text_content = []
        self.links = []
        self.current_tag = ""
        self.in_title = False
        self.in_script = False
        self.in_style = False
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()
        
        if tag.lower() == 'title':
            self.in_title = True
        elif tag.lower() in ['script', 'style']:
            self.in_script = True
            self.in_style = True
        elif tag.lower() == 'a':
            # Extract link URL
            href = None
            for attr_name, attr_value in attrs:
                if attr_name.lower() == 'href':
                    href = attr_value
                    break
            if href:
                self.current_link_url = href
        elif tag.lower() in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']:
            self.text_content.append('\n')
        elif tag.lower() == 'br':
            self.text_content.append('\n')
    
    def handle_endtag(self, tag):
        if tag.lower() == 'title':
            self.in_title = False
        elif tag.lower() in ['script', 'style']:
            self.in_script = False
            self.in_style = False
        elif tag.lower() == 'a' and hasattr(self, 'current_link_url'):
            # Save the link
            link_text = ''.join(self.text_content[-10:]).strip()  # Get recent text as link text
            if link_text and self.current_link_url:
                self.links.append((link_text, self.current_link_url))
            delattr(self, 'current_link_url')
        elif tag.lower() in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.text_content.append('\n\n')
    
    def handle_data(self, data):
        if self.in_title:
            self.title += data.strip()
        elif not (self.in_script or self.in_style):
            # Clean up the text
            cleaned_data = ' '.join(data.split())  # Remove extra whitespace
            if cleaned_data:
                self.text_content.append(cleaned_data + ' ')
    
    def get_text(self):
        """Get the extracted text content"""
        text = ''.join(self.text_content)
        # Clean up extra newlines and spaces
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Max 2 consecutive newlines
        text = re.sub(r' +', ' ', text)  # Remove extra spaces
        return text.strip()

class BLSCBrowser:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BLSC Web Browser")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2d2d30')
        
        # Browser data
        self.history = []
        self.bookmarks = []
        self.current_url = ""
        self.home_page = "https://www.google.com"
        
        # Load saved data
        self.load_data()
        
        # Setup UI
        self.setup_ui()
        
        # Load home page
        self.navigate_to(self.home_page)
    
    def setup_ui(self):
        """Setup the browser user interface"""
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2d2d30')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top toolbar
        self.create_toolbar(main_frame)
        
        # Address bar frame
        self.create_address_bar(main_frame)
        
        # Content area with tabs
        self.create_content_area(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_toolbar(self, parent):
        """Create the browser toolbar"""
        toolbar = tk.Frame(parent, bg='#323233', height=40)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        toolbar.pack_propagate(False)
        
        # Navigation buttons
        btn_style = {
            'bg': '#0e639c',
            'fg': 'white',
            'font': ('Arial', 10, 'bold'),
            'relief': 'flat',
            'padx': 10,
            'pady': 5,
            'cursor': 'hand2'
        }
        
        # Back button
        self.back_btn = tk.Button(toolbar, text="◀ Back", command=self.go_back, **btn_style)
        self.back_btn.pack(side=tk.LEFT, padx=(10, 2))
        
        # Forward button
        self.forward_btn = tk.Button(toolbar, text="Forward ▶", command=self.go_forward, **btn_style)
        self.forward_btn.pack(side=tk.LEFT, padx=2)
        
        # Refresh button
        refresh_btn = tk.Button(toolbar, text="🔄 Refresh", command=self.refresh_page, **btn_style)
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        # Home button
        home_btn = tk.Button(toolbar, text="🏠 Home", command=self.go_home, **btn_style)
        home_btn.pack(side=tk.LEFT, padx=2)
        
        # Separator
        separator = tk.Frame(toolbar, width=2, bg='#555')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Bookmarks button
        bookmarks_btn = tk.Button(toolbar, text="⭐ Bookmarks", command=self.show_bookmarks, **btn_style)
        bookmarks_btn.pack(side=tk.LEFT, padx=2)
        
        # History button
        history_btn = tk.Button(toolbar, text="📚 History", command=self.show_history, **btn_style)
        history_btn.pack(side=tk.LEFT, padx=2)
        
        # Downloads button
        downloads_btn = tk.Button(toolbar, text="⬇️ Downloads", command=self.show_downloads, **btn_style)
        downloads_btn.pack(side=tk.LEFT, padx=2)
        
        # Settings button
        settings_btn = tk.Button(toolbar, text="⚙️ Settings", command=self.show_settings, **btn_style)
        settings_btn.pack(side=tk.RIGHT, padx=(2, 10))
    
    def create_address_bar(self, parent):
        """Create the address bar"""
        address_frame = tk.Frame(parent, bg='#2d2d30', height=50)
        address_frame.pack(fill=tk.X, pady=(0, 5))
        address_frame.pack_propagate(False)
        
        # URL entry
        url_frame = tk.Frame(address_frame, bg='#3c3c3c', relief='solid', bd=1)
        url_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Security indicator
        self.security_label = tk.Label(url_frame, text="🔒", bg='#3c3c3c', fg='#4ec9b0', font=('Arial', 12))
        self.security_label.pack(side=tk.LEFT, padx=(10, 5))
        
        # URL entry field
        self.url_entry = tk.Entry(url_frame, bg='#3c3c3c', fg='white', font=('Arial', 12), 
                                 relief='flat', insertbackground='white')
        self.url_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=8)
        self.url_entry.bind('<Return>', self.navigate_from_entry)
        
        # Go button
        go_btn = tk.Button(url_frame, text="Go", bg='#0e639c', fg='white', 
                          font=('Arial', 10, 'bold'), relief='flat', 
                          command=self.navigate_from_entry, cursor='hand2')
        go_btn.pack(side=tk.RIGHT, padx=(5, 10), pady=5)
        
        # Add bookmark button
        bookmark_btn = tk.Button(url_frame, text="⭐", bg='#3c3c3c', fg='#ffd700', 
                                font=('Arial', 12), relief='flat', 
                                command=self.add_bookmark, cursor='hand2')
        bookmark_btn.pack(side=tk.RIGHT, padx=2)
    
    def create_content_area(self, parent):
        """Create the main content area"""
        content_frame = tk.Frame(parent, bg='#1e1e1e', relief='solid', bd=1)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create first tab
        self.create_new_tab("New Tab")
    
    def create_new_tab(self, title="New Tab"):
        """Create a new browser tab"""
        tab_frame = tk.Frame(self.notebook, bg='#1e1e1e')
        
        # Web content area (using ScrolledText as a simple web viewer)
        self.web_content = scrolledtext.ScrolledText(
            tab_frame, 
            bg='white', 
            fg='black', 
            font=('Arial', 11),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.web_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.notebook.add(tab_frame, text=title)
        return tab_frame
    
    def create_status_bar(self, parent):
        """Create the status bar"""
        status_frame = tk.Frame(parent, bg='#007acc', height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready", bg='#007acc', 
                                   fg='white', font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=2)
        
        # Connection status
        self.connection_label = tk.Label(status_frame, text="🌐 Online", bg='#007acc', 
                                       fg='white', font=('Arial', 9))
        self.connection_label.pack(side=tk.RIGHT, padx=10, pady=2)
    
    def navigate_to(self, url):
        """Navigate to a specific URL"""
        if not url:
            return
            
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            if '.' in url:
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
        
        # Load page content
        self.load_page(url)
        
        # Add to history
        self.add_to_history(url)
    
    def load_page(self, url):
        """Load page content directly in the browser"""
        self.status_label.config(text=f"Loading {url}...")
        
        def load_in_thread():
            try:
                # Create request with proper headers
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'BLSC-Browser/1.0 (Python/Tkinter)')
                req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
                
                with urllib.request.urlopen(req, timeout=15) as response:
                    content_type = response.headers.get('content-type', 'text/html')
                    status_code = response.getcode()
                    
                    # Read the full content
                    raw_content = response.read()
                    
                    # Try to decode with different encodings
                    content = ""
                    for encoding in ['utf-8', 'latin-1', 'cp1252']:
                        try:
                            content = raw_content.decode(encoding)
                            break
                        except:
                            continue
                    
                    if not content:
                        content = raw_content.decode('utf-8', errors='ignore')
                    
                    # Parse and render the HTML
                    if 'text/html' in content_type:
                        rendered_content = self.render_html(content, url)
                    else:
                        # For non-HTML content, show as plain text
                        rendered_content = f"Content Type: {content_type}\n\n{content[:5000]}"
                    
                    # Extract title
                    title = self.extract_title(content)
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.update_page_content(rendered_content, f"✅ {title}"))
                    
            except urllib.error.HTTPError as e:
                error_msg = f"HTTP Error {e.code}: {e.reason}\n\nURL: {url}"
                self.root.after(0, lambda: self.update_page_content(error_msg, f"❌ HTTP {e.code}"))
                
            except urllib.error.URLError as e:
                error_msg = f"Connection Error: {e.reason}\n\nURL: {url}\n\nCheck your internet connection."
                self.root.after(0, lambda: self.update_page_content(error_msg, "❌ Connection Error"))
                
            except Exception as e:
                error_msg = f"Error loading page: {str(e)}\n\nURL: {url}"
                self.root.after(0, lambda: self.update_page_content(error_msg, f"❌ Error"))
        
        # Start loading in background thread
        threading.Thread(target=load_in_thread, daemon=True).start()
    
    def extract_title(self, html_content):
        """Extract title from HTML content"""
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = html.unescape(title_match.group(1).strip())
            return title[:100]  # Limit title length
        return "Untitled Page"
    
    def render_html(self, html_content, base_url):
        """Render HTML content as readable text"""
        try:
            # Simple HTML parser to extract readable content
            parser = SimpleHTMLParser()
            parser.feed(html_content)
            
            # Get the parsed content
            title = parser.title or self.extract_title(html_content)
            text_content = parser.get_text()
            links = parser.links
            
            # Format the content for display
            rendered = f"""
🌐 {title}
{'=' * len(title)}

📍 URL: {base_url}
🕒 Loaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📄 CONTENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{text_content}

"""
            
            # Add links section if there are links
            if links:
                rendered += "\n🔗 LINKS FOUND:\n"
                rendered += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                for i, (link_text, link_url) in enumerate(links[:20], 1):  # Show first 20 links
                    rendered += f"{i}. {link_text}\n   → {link_url}\n\n"
                
                if len(links) > 20:
                    rendered += f"... and {len(links) - 20} more links\n"
            
            return rendered
            
        except Exception as e:
            # Fallback: show raw HTML with some formatting
            return f"Error parsing HTML: {e}\n\nRaw content:\n{html_content[:3000]}..."
    
    def update_page_content(self, content, status):
        """Update the page content display"""
        self.web_content.config(state=tk.NORMAL)
        self.web_content.delete(1.0, tk.END)
        self.web_content.insert(1.0, content)
        self.web_content.config(state=tk.DISABLED)
        self.status_label.config(text=status)
    
    def navigate_from_entry(self, event=None):
        """Navigate to URL from entry field"""
        url = self.url_entry.get().strip()
        self.navigate_to(url)
    
    def go_back(self):
        """Go back in history"""
        if len(self.history) > 1:
            # Remove current page
            self.history.pop()
            # Go to previous page
            if self.history:
                prev_url = self.history.pop()  # Will be re-added by navigate_to
                self.navigate_to(prev_url)
    
    def go_forward(self):
        """Go forward in history (simplified)"""
        messagebox.showinfo("Forward", "Forward functionality would be implemented with a more complex history system")
    
    def refresh_page(self):
        """Refresh current page"""
        if self.current_url:
            self.navigate_to(self.current_url)
    
    def go_home(self):
        """Go to home page"""
        self.navigate_to(self.home_page)
    
    def add_to_history(self, url):
        """Add URL to history"""
        if url and (not self.history or self.history[-1] != url):
            self.history.append(url)
            # Keep only last 100 entries
            if len(self.history) > 100:
                self.history = self.history[-100:]
    
    def add_bookmark(self):
        """Add current page to bookmarks"""
        if self.current_url:
            title = simpledialog.askstring("Bookmark", "Enter bookmark title:", 
                                         initialvalue=self.current_url)
            if title:
                bookmark = {"title": title, "url": self.current_url, "date": datetime.now().isoformat()}
                self.bookmarks.append(bookmark)
                self.save_data()
                messagebox.showinfo("Bookmark", f"Bookmarked: {title}")
    
    def show_bookmarks(self):
        """Show bookmarks window"""
        bookmarks_window = tk.Toplevel(self.root)
        bookmarks_window.title("Bookmarks")
        bookmarks_window.geometry("600x400")
        bookmarks_window.configure(bg='#2d2d30')
        
        # Bookmarks list
        listbox = tk.Listbox(bookmarks_window, bg='#3c3c3c', fg='white', 
                           font=('Arial', 11), selectbackground='#0e639c')
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
        """Show history window"""
        history_window = tk.Toplevel(self.root)
        history_window.title("History")
        history_window.geometry("600x400")
        history_window.configure(bg='#2d2d30')
        
        # History list
        listbox = tk.Listbox(history_window, bg='#3c3c3c', fg='white', 
                           font=('Arial', 11), selectbackground='#0e639c')
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
    
    def show_downloads(self):
        """Show downloads window"""
        messagebox.showinfo("Downloads", "Downloads functionality would be implemented here")
    
    def show_settings(self):
        """Show settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x300")
        settings_window.configure(bg='#2d2d30')
        
        # Home page setting
        tk.Label(settings_window, text="Home Page:", bg='#2d2d30', fg='white', 
                font=('Arial', 12)).pack(pady=10)
        
        home_entry = tk.Entry(settings_window, font=('Arial', 11), width=50)
        home_entry.pack(pady=5)
        home_entry.insert(0, self.home_page)
        
        def save_settings():
            self.home_page = home_entry.get()
            self.save_data()
            messagebox.showinfo("Settings", "Settings saved!")
            settings_window.destroy()
        
        tk.Button(settings_window, text="Save", command=save_settings, 
                 bg='#0e639c', fg='white', font=('Arial', 11, 'bold')).pack(pady=20)
    
    def save_data(self):
        """Save browser data to file"""
        try:
            data = {
                'bookmarks': self.bookmarks,
                'home_page': self.home_page,
                'history': self.history[-50:]  # Save last 50 history items
            }
            with open('browser_data.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Load browser data from file"""
        try:
            if os.path.exists('browser_data.json'):
                with open('browser_data.json', 'r') as f:
                    data = json.load(f)
                    self.bookmarks = data.get('bookmarks', [])
                    self.home_page = data.get('home_page', 'https://www.google.com')
                    self.history = data.get('history', [])
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def run(self):
        """Start the browser"""
        # Save data on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle browser closing"""
        self.save_data()
        self.root.destroy()

def main():
    """Main function to run the browser"""
    print("🌐 Starting BLSC Web Browser...")
    print("📍 Created by: Benayas Leulseged Software Community")
    print("🚀 Loading browser interface...")
    
    browser = BLSCBrowser()
    browser.run()

if __name__ == "__main__":
    main()