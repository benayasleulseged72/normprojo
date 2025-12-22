let currentTab = 0;
let tabs = [{ url: '', title: 'New Tab', history: [], historyIndex: -1, favicon: '🏠' }];
let bookmarks = JSON.parse(localStorage.getItem('blscBookmarks')) || [];
let passwords = JSON.parse(localStorage.getItem('blscPasswords')) || [];
let downloads = JSON.parse(localStorage.getItem('blscDownloads')) || [];
let savedPages = JSON.parse(localStorage.getItem('blscSavedPages')) || [];
let quickLinks = JSON.parse(localStorage.getItem('blscQuickLinks')) || [
    { name: 'Bing', url: 'https://www.bing.com', icon: '🔍', iconType: 'auto' },
    { name: 'Wikipedia', url: 'https://www.wikipedia.org', icon: '📚', iconType: 'auto' },
    { name: 'W3Schools', url: 'https://www.w3schools.com', icon: '💻', iconType: 'auto' },
    { name: 'Stack Overflow', url: 'https://www.stackoverflow.com', icon: '❓', iconType: 'auto' },
    { name: 'Google', url: 'https://www.google.com', icon: '🔗', iconType: 'auto' },
    { name: 'YouTube', url: 'https://www.youtube.com', icon: '📺', iconType: 'auto' },
    { name: 'GitHub', url: 'https://www.github.com', icon: '💾', iconType: 'auto' },
    { name: 'More Sites', url: '../impweb/impweb.html', icon: '⭐', iconType: 'emoji' }
];
let currentURL = '';
let isDarkMode = localStorage.getItem('blscTheme') !== 'light';

function init() {
    renderHomePage();
    updateNavigationButtons();
    applyTheme();
}

function toggleTheme() {
    isDarkMode = !isDarkMode;
    localStorage.setItem('blscTheme', isDarkMode ? 'dark' : 'light');
    applyTheme();
}

function applyTheme() {
    const root = document.documentElement;
    const themeBtn = document.getElementById('themeToggle');
    
    if (isDarkMode) {
        root.style.setProperty('--bg-primary', '#202124');
        root.style.setProperty('--bg-secondary', '#2d2e30');
        root.style.setProperty('--bg-tertiary', '#3c4043');
        root.style.setProperty('--bg-hover', '#5f6368');
        root.style.setProperty('--text-primary', '#e8eaed');
        root.style.setProperty('--text-secondary', '#9aa0a6');
        root.style.setProperty('--accent', '#8ab4f8');
        themeBtn.textContent = '🌙';
        themeBtn.title = 'Switch to Light Mode';
    } else {
        root.style.setProperty('--bg-primary', '#ffffff');
        root.style.setProperty('--bg-secondary', '#f1f3f4');
        root.style.setProperty('--bg-tertiary', '#e8eaed');
        root.style.setProperty('--bg-hover', '#d2d4d6');
        root.style.setProperty('--text-primary', '#202124');
        root.style.setProperty('--text-secondary', '#5f6368');
        root.style.setProperty('--accent', '#1a73e8');
        themeBtn.textContent = '☀️';
        themeBtn.title = 'Switch to Dark Mode';
    }
}

function renderHomePage() {
    const homePage = document.getElementById('homePage');
    homePage.innerHTML = `
        <img src="1.png" alt="BLSC Logo" class="home-logo">
        <h1 class="home-title">BLSC Browser</h1>
        <p class="home-subtitle">Fast, Secure, and Powerful</p>
        <div class="quick-links" id="quickLinksContainer"></div>
    `;
    renderQuickLinks();
}

function renderQuickLinks() {
    const container = document.getElementById('quickLinksContainer');
    container.innerHTML = quickLinks.map((link, index) => {
        let iconHTML = '';
        
        if (link.iconType === 'image') {
            iconHTML = `<img src="${link.icon}" style="width: 32px; height: 32px; border-radius: 6px;" onerror="this.parentElement.innerHTML='🌐'">`;
        } else if (link.iconType === 'auto') {
            try {
                const urlObj = new URL(link.url);
                const faviconUrl = `https://www.google.com/s2/favicons?domain=${urlObj.hostname}&sz=64`;
                iconHTML = `<img src="${faviconUrl}" style="width: 32px; height: 32px;" onerror="this.parentElement.innerHTML='🌐'">`;
            } catch {
                iconHTML = `<span style="font-size: 32px;">🌐</span>`;
            }
        } else {
            iconHTML = `<span style="font-size: 32px;">${link.icon}</span>`;
        }
        
        return `
            <div class="quick-link" onclick="navigateToQuickLink('${link.url}', event)">
                <button class="quick-link-delete" onclick="deleteQuickLink(${index}, event)">×</button>
                <div class="quick-link-icon">${iconHTML}</div>
                <div class="quick-link-name">${link.name}</div>
            </div>
        `;
    }).join('') + `
        <div class="quick-link add-link-btn" onclick="showAddLinkModal()">+</div>
    `;
}

function navigateToQuickLink(url, event) {
    event.stopPropagation();
    loadURL(url);
}

function deleteQuickLink(index, event) {
    event.stopPropagation();
    if (confirm('Delete this quick link?')) {
        quickLinks.splice(index, 1);
        localStorage.setItem('blscQuickLinks', JSON.stringify(quickLinks));
        renderQuickLinks();
    }
}

function showAddLinkModal() {
    showModal('Add Quick Link', `
        <div class="form-group">
            <label class="form-label">Name</label>
            <input type="text" class="form-input" id="linkName" placeholder="e.g., Facebook">
        </div>
        <div class="form-group">
            <label class="form-label">URL</label>
            <input type="text" class="form-input" id="linkURL" placeholder="https://example.com">
        </div>
        <div class="form-group">
            <label class="form-label">Icon Option</label>
            <select class="form-input" id="iconType" onchange="toggleIconInput()">
                <option value="emoji">Emoji</option>
                <option value="upload">Upload Image</option>
                <option value="auto">Auto (from website)</option>
            </select>
        </div>
        <div class="form-group" id="emojiInput">
            <label class="form-label">Icon (emoji)</label>
            <input type="text" class="form-input" id="linkIcon" placeholder="🌐" maxlength="2">
        </div>
        <div class="form-group" id="uploadInput" style="display: none;">
            <label class="form-label">Upload Icon</label>
            <input type="file" class="form-input" id="linkIconFile" accept="image/*">
            <div id="iconPreview" style="margin-top: 10px; text-align: center;"></div>
        </div>
        <button class="btn btn-primary" onclick="addQuickLink()">Add Link</button>
    `);
}

function toggleIconInput() {
    const iconType = document.getElementById('iconType').value;
    const emojiInput = document.getElementById('emojiInput');
    const uploadInput = document.getElementById('uploadInput');
    
    if (iconType === 'emoji') {
        emojiInput.style.display = 'block';
        uploadInput.style.display = 'none';
    } else if (iconType === 'upload') {
        emojiInput.style.display = 'none';
        uploadInput.style.display = 'block';
        
        const fileInput = document.getElementById('linkIconFile');
        fileInput.onchange = function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    document.getElementById('iconPreview').innerHTML = 
                        `<img src="${event.target.result}" style="width: 48px; height: 48px; border-radius: 8px;">`;
                };
                reader.readAsDataURL(file);
            }
        };
    } else {
        emojiInput.style.display = 'none';
        uploadInput.style.display = 'none';
    }
}

function addQuickLink() {
    const name = document.getElementById('linkName').value.trim();
    const url = document.getElementById('linkURL').value.trim();
    const iconType = document.getElementById('iconType').value;
    
    if (!name || !url) {
        alert('Please fill in name and URL');
        return;
    }
    
    let icon = '🌐';
    
    if (iconType === 'emoji') {
        icon = document.getElementById('linkIcon').value.trim() || '🌐';
        quickLinks.push({ name, url, icon, iconType: 'emoji' });
        localStorage.setItem('blscQuickLinks', JSON.stringify(quickLinks));
        renderQuickLinks();
        closeModal();
    } else if (iconType === 'upload') {
        const fileInput = document.getElementById('linkIconFile');
        if (fileInput.files.length > 0) {
            const reader = new FileReader();
            reader.onload = function(event) {
                quickLinks.push({ name, url, icon: event.target.result, iconType: 'image' });
                localStorage.setItem('blscQuickLinks', JSON.stringify(quickLinks));
                renderQuickLinks();
                closeModal();
            };
            reader.readAsDataURL(fileInput.files[0]);
        } else {
            alert('Please upload an icon image');
        }
    } else {
        quickLinks.push({ name, url, icon, iconType: 'auto' });
        localStorage.setItem('blscQuickLinks', JSON.stringify(quickLinks));
        renderQuickLinks();
        closeModal();
    }
}

function handleAddressBar(event) {
    if (event.key === 'Enter') {
        let url = document.getElementById('addressBar').value.trim();
        if (!url) return;
        
        // Check if it's a local address
        const isLocal = url.startsWith('localhost') || 
                       url.startsWith('127.0.0.1') || 
                       url.match(/^192\.168\.\d+\.\d+/) ||
                       url.match(/^10\.\d+\.\d+\.\d+/) ||
                       url.match(/^172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+/);
        
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            if (isLocal) {
                // For local addresses, use http:// by default
                url = 'http://' + url;
            } else if (url.includes('.') && !url.includes(' ')) {
                url = 'https://' + url;
            } else {
                // Use Bing for search instead of Google
                url = 'https://www.bing.com/search?q=' + encodeURIComponent(url);
            }
        }
        
        // Special handling for YouTube
        if (url.includes('youtube.com/watch')) {
            const videoId = extractYouTubeId(url);
            if (videoId) {
                loadYouTubeEmbed(videoId);
                return;
            }
        }
        
        // Special handling for Google search
        if (url.includes('google.com/search')) {
            const query = extractGoogleQuery(url);
            if (query) {
                // Redirect to Bing search which works in iframe
                url = 'https://www.bing.com/search?q=' + encodeURIComponent(query);
            }
        }
        
        loadURL(url);
    }
}

function extractYouTubeId(url) {
    const match = url.match(/[?&]v=([^&]+)/);
    return match ? match[1] : null;
}

function extractGoogleQuery(url) {
    const match = url.match(/[?&]q=([^&]+)/);
    return match ? decodeURIComponent(match[1]) : null;
}

function loadYouTubeEmbed(videoId) {
    const frame = document.getElementById('browserFrame');
    const homePage = document.getElementById('homePage');
    const errorPage = document.getElementById('errorPage');
    const addressBar = document.getElementById('addressBar');
    
    homePage.style.display = 'none';
    errorPage.style.display = 'none';
    frame.style.display = 'block';
    
    const embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
    frame.src = embedUrl;
    addressBar.value = `https://www.youtube.com/watch?v=${videoId}`;
    
    currentURL = embedUrl;
    tabs[currentTab].url = embedUrl;
    tabs[currentTab].title = 'YouTube';
    updateTabDisplay();
}

function loadURL(url) {
    const frame = document.getElementById('browserFrame');
    const homePage = document.getElementById('homePage');
    const errorPage = document.getElementById('errorPage');
    const loadingBar = document.getElementById('loadingBar');
    const addressBar = document.getElementById('addressBar');
    
    currentURL = url;
    loadingBar.classList.add('active');
    homePage.style.display = 'none';
    errorPage.style.display = 'none';
    frame.style.display = 'block';
    
    // Try direct load first
    frame.src = url;
    addressBar.value = url;
    tabs[currentTab].url = url;
    updateTabTitle(url);
    addToHistory(url);
    updateBookmarkButton();
    
    let loadTimeout;
    let hasLoaded = false;
    
    frame.onload = function() {
        hasLoaded = true;
        loadingBar.classList.remove('active');
        clearTimeout(loadTimeout);
    };
    
    frame.onerror = function() {
        loadingBar.classList.remove('active');
        showError();
    };
    
    // Check if iframe loaded after 3 seconds
    loadTimeout = setTimeout(() => {
        loadingBar.classList.remove('active');
        
        // Try to detect if iframe is blocked
        try {
            const frameDoc = frame.contentDocument || frame.contentWindow.document;
            if (!frameDoc || frameDoc.body.innerHTML === '') {
                // Iframe is likely blocked, show error with proxy option
                showErrorWithProxy(url);
            }
        } catch (e) {
            // Cross-origin error means it might have loaded
            if (!hasLoaded) {
                // Give it more time or show error
                setTimeout(() => {
                    if (!hasLoaded) {
                        showErrorWithProxy(url);
                    }
                }, 2000);
            }
        }
    }, 3000);
}

function showError() {
    const frame = document.getElementById('browserFrame');
    const errorPage = document.getElementById('errorPage');
    
    frame.style.display = 'none';
    errorPage.style.display = 'flex';
    errorPage.innerHTML = `
        <div class="error-icon">🔒</div>
        <h2 class="error-title">Refused to Connect</h2>
        <p class="error-message">
            <strong>Why this happens:</strong><br>
            This website blocks embedding in iframes for security (X-Frame-Options policy).<br><br>
            <strong>Blocked sites include:</strong> YouTube, Google, Facebook, Instagram, Twitter, GitHub, Netflix, Amazon, TikTok, LinkedIn, Reddit, and many others.<br><br>
            <strong>Sites that work:</strong> Wikipedia, W3Schools, Bing, Stack Overflow, and most smaller websites.<br><br>
            This is a browser security feature that cannot be bypassed in web apps.
        </p>
        <button class="open-external-btn" onclick="openInNewWindow()">
            Open in New Window →
        </button>
        <button class="open-external-btn" onclick="goHome()" style="background: #5f6368; margin-left: 10px;">
            ← Go Back Home
        </button>
    `;
}

function showErrorWithProxy(url) {
    const frame = document.getElementById('browserFrame');
    const errorPage = document.getElementById('errorPage');
    
    frame.style.display = 'none';
    errorPage.style.display = 'flex';
    errorPage.innerHTML = `
        <div class="error-icon">🔒</div>
        <h2 class="error-title">Website Blocked</h2>
        <p class="error-message">
            This website refuses to load in the browser due to security policies.<br><br>
            <strong>Options:</strong>
        </p>
        <div style="display: flex; flex-direction: column; gap: 10px; max-width: 400px;">
            <button class="open-external-btn" onclick="openInNewWindow()">
                🌐 Open in New Browser Tab
            </button>
            <button class="open-external-btn" onclick="tryProxy('${url}')" style="background: #f9ab00;">
                🔄 Try Proxy (May Work)
            </button>
            <button class="open-external-btn" onclick="tryMobileView('${url}')" style="background: #34a853;">
                📱 Try Mobile View
            </button>
            <button class="open-external-btn" onclick="goHome()" style="background: #5f6368;">
                ← Go Back Home
            </button>
        </div>
        <p style="font-size: 12px; color: var(--text-secondary); margin-top: 20px;">
            Note: Proxy and mobile view may not work for all sites due to browser security.
        </p>
    `;
}

function tryProxy(url) {
    const frame = document.getElementById('browserFrame');
    const errorPage = document.getElementById('errorPage');
    const loadingBar = document.getElementById('loadingBar');
    
    errorPage.style.display = 'none';
    frame.style.display = 'block';
    loadingBar.classList.add('active');
    
    // Try using a web proxy service
    const proxyUrl = `https://cors-anywhere.herokuapp.com/${url}`;
    
    frame.src = proxyUrl;
    
    setTimeout(() => {
        loadingBar.classList.remove('active');
    }, 5000);
}

function tryMobileView(url) {
    const frame = document.getElementById('browserFrame');
    const errorPage = document.getElementById('errorPage');
    const loadingBar = document.getElementById('loadingBar');
    
    errorPage.style.display = 'none';
    frame.style.display = 'block';
    loadingBar.classList.add('active');
    
    // Try mobile version of the site
    let mobileUrl = url;
    if (url.includes('youtube.com')) {
        mobileUrl = url.replace('www.youtube.com', 'm.youtube.com');
    } else if (url.includes('twitter.com')) {
        mobileUrl = url.replace('twitter.com', 'mobile.twitter.com');
    } else if (url.includes('facebook.com')) {
        mobileUrl = url.replace('www.facebook.com', 'm.facebook.com');
    }
    
    frame.src = mobileUrl;
    
    setTimeout(() => {
        loadingBar.classList.remove('active');
    }, 3000);
}

function openInNewWindow() {
    if (currentURL) {
        window.open(currentURL, '_blank');
    }
}

function navigateTo(url, event) {
    if (event) event.preventDefault();
    loadURL(url);
}

function goBack() {
    const tab = tabs[currentTab];
    if (tab.historyIndex > 0) {
        tab.historyIndex--;
        loadURL(tab.history[tab.historyIndex]);
        updateNavigationButtons();
    }
}

function goForward() {
    const tab = tabs[currentTab];
    if (tab.historyIndex < tab.history.length - 1) {
        tab.historyIndex++;
        loadURL(tab.history[tab.historyIndex]);
        updateNavigationButtons();
    }
}

function reloadPage() {
    const frame = document.getElementById('browserFrame');
    if (frame.src) {
        frame.src = frame.src;
    }
}

function goHome() {
    const frame = document.getElementById('browserFrame');
    const homePage = document.getElementById('homePage');
    const errorPage = document.getElementById('errorPage');
    const addressBar = document.getElementById('addressBar');
    
    frame.style.display = 'none';
    errorPage.style.display = 'none';
    homePage.style.display = 'flex';
    addressBar.value = '';
    currentURL = '';
    
    tabs[currentTab].url = '';
    tabs[currentTab].title = 'New Tab';
    updateTabDisplay();
    updateBookmarkButton();
}

function addToHistory(url) {
    const tab = tabs[currentTab];
    tab.history = tab.history.slice(0, tab.historyIndex + 1);
    tab.history.push(url);
    tab.historyIndex = tab.history.length - 1;
    updateNavigationButtons();
}

function updateNavigationButtons() {
    const tab = tabs[currentTab];
    document.getElementById('backBtn').disabled = tab.historyIndex <= 0;
    document.getElementById('forwardBtn').disabled = tab.historyIndex >= tab.history.length - 1;
}

function updateTabTitle(url) {
    try {
        const urlObj = new URL(url);
        const domain = urlObj.hostname.replace('www.', '');
        tabs[currentTab].title = domain;
        tabs[currentTab].favicon = `https://www.google.com/s2/favicons?domain=${urlObj.hostname}&sz=32`;
    } catch {
        tabs[currentTab].title = 'New Tab';
        tabs[currentTab].favicon = '🏠';
    }
    updateTabDisplay();
}

function updateTabDisplay() {
    const tabElements = document.querySelectorAll('.tab');
    tabElements.forEach((tab, index) => {
        const titleEl = tab.querySelector('.tab-title');
        const faviconEl = tab.querySelector('.tab-favicon');
        if (titleEl && tabs[index]) {
            titleEl.textContent = tabs[index].title;
        }
        if (faviconEl && tabs[index]) {
            const favicon = tabs[index].favicon || '🏠';
            if (favicon.startsWith('http')) {
                faviconEl.innerHTML = `<img src="${favicon}" style="width: 16px; height: 16px;" onerror="this.parentElement.textContent='🌐'">`;
            } else {
                faviconEl.textContent = favicon;
            }
        }
    });
}

function addNewTab() {
    tabs.push({ url: '', title: 'New Tab', history: [], historyIndex: -1, favicon: '🏠' });
    currentTab = tabs.length - 1;
    
    const tabBar = document.querySelector('.tab-bar');
    const newTabBtn = document.querySelector('.new-tab-btn');
    
    const tabEl = document.createElement('div');
    tabEl.className = 'tab active';
    tabEl.setAttribute('data-tab', currentTab);
    tabEl.innerHTML = `
        <span class="tab-favicon">🏠</span>
        <span class="tab-title">New Tab</span>
        <button class="tab-close" onclick="closeTab(${currentTab}, event)">×</button>
    `;
    tabEl.onclick = () => switchTab(currentTab);
    
    tabBar.insertBefore(tabEl, newTabBtn);
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tabEl.classList.add('active');
    goHome();
}

function switchTab(index) {
    currentTab = index;
    document.querySelectorAll('.tab').forEach((t, i) => {
        t.classList.toggle('active', i === index);
    });
    
    const tab = tabs[index];
    if (tab.url) {
        loadURL(tab.url);
    } else {
        goHome();
    }
}

function closeTab(index, event) {
    event.stopPropagation();
    if (tabs.length === 1) {
        goHome();
        return;
    }
    
    tabs.splice(index, 1);
    const tabElements = document.querySelectorAll('.tab');
    tabElements[index].remove();
    
    if (currentTab >= tabs.length) {
        currentTab = tabs.length - 1;
    }
    switchTab(currentTab);
}

function toggleBookmark() {
    const url = document.getElementById('addressBar').value;
    if (!url) return;
    
    const index = bookmarks.findIndex(b => b.url === url);
    if (index > -1) {
        bookmarks.splice(index, 1);
        alert('Bookmark removed!');
    } else {
        const title = tabs[currentTab].title || 'Untitled';
        bookmarks.push({ title, url, date: new Date().toISOString() });
        alert('Bookmark added!');
    }
    
    localStorage.setItem('blscBookmarks', JSON.stringify(bookmarks));
    updateBookmarkButton();
}

function updateBookmarkButton() {
    const url = document.getElementById('addressBar').value;
    const starBtn = document.querySelector('.star-btn');
    const isBookmarked = bookmarks.some(b => b.url === url);
    starBtn.classList.toggle('active', isBookmarked);
    starBtn.textContent = isBookmarked ? '★' : '☆';
}

function toggleMenu() {
    const panel = document.getElementById('menuPanel');
    panel.classList.toggle('active');
    
    if (panel.classList.contains('active')) {
        panel.innerHTML = `
            <div class="menu-header">
                Browser Menu
                <button class="menu-close" onclick="toggleMenu()">×</button>
            </div>
            <div class="menu-content">
                <div class="menu-item" onclick="showBookmarks()">
                    <span class="menu-item-icon">⭐</span>
                    <span class="menu-item-text">Bookmarks (${bookmarks.length})</span>
                </div>
                <div class="menu-item" onclick="showHistory()">
                    <span class="menu-item-icon">🕒</span>
                    <span class="menu-item-text">History</span>
                </div>
                <div class="menu-item" onclick="showDownloads()">
                    <span class="menu-item-icon">⬇️</span>
                    <span class="menu-item-text">Downloads (${downloads.length})</span>
                </div>
                <div class="menu-item" onclick="showSavedPages()">
                    <span class="menu-item-icon">�</sspan>
                    <span class="menu-item-text">Saved Pages (${savedPages.length})</span>
                </div>
                <div class="menu-item" onclick="showPasswords()">
                    <span class="menu-item-icon">🔑</span>
                    <span class="menu-item-text">Passwords (${passwords.length})</span>
                </div>
                <div class="menu-item" onclick="toggleFullscreen(); toggleMenu();">
                    <span class="menu-item-icon">⛶</span>
                    <span class="menu-item-text">Fullscreen</span>
                </div>
                <div class="menu-item" onclick="showSettings()">
                    <span class="menu-item-icon">⚙️</span>
                    <span class="menu-item-text">Settings</span>
                </div>
                <div class="menu-item" onclick="clearAllData()">
                    <span class="menu-item-icon">🗑️</span>
                    <span class="menu-item-text">Clear All Data</span>
                </div>
            </div>
        `;
    }
}

function showBookmarks() {
    toggleMenu();
    showModal('Bookmarks', `
        <div class="modal-body">
            ${bookmarks.length === 0 ? '<p style="color: #9aa0a6;">No bookmarks yet</p>' : 
                bookmarks.map((b, i) => `
                    <div class="list-item">
                        <div class="list-item-text" onclick="loadURL('${b.url}'); closeModal();" style="cursor: pointer;">
                            <strong>${b.title}</strong><br>
                            <small style="color: #9aa0a6;">${b.url}</small>
                        </div>
                        <div class="list-item-actions">
                            <button class="btn btn-primary" onclick="saveSpecificPage('${b.url}', '${b.title}')">Save</button>
                            <button class="btn btn-danger" onclick="deleteBookmark(${i})">Delete</button>
                        </div>
                    </div>
                `).join('')
            }
        </div>
    `);
}

function saveSpecificPage(url, title) {
    alert('Loading page to save...');
    closeModal();
    loadURL(url);
    setTimeout(() => {
        savePageOffline();
    }, 3000);
}

function deleteBookmark(index) {
    bookmarks.splice(index, 1);
    localStorage.setItem('blscBookmarks', JSON.stringify(bookmarks));
    showBookmarks();
}

function showHistory() {
    toggleMenu();
    const allHistory = tabs.flatMap(t => t.history).filter((v, i, a) => a.indexOf(v) === i).reverse();
    showModal('History', `
        <div class="modal-body">
            ${allHistory.length === 0 ? '<p style="color: #9aa0a6;">No history yet</p>' : 
                allHistory.map(url => `
                    <div class="list-item">
                        <div class="list-item-text" onclick="loadURL('${url}')" style="cursor: pointer;">
                            ${url}
                        </div>
                    </div>
                `).join('')
            }
            <button class="btn btn-danger" onclick="clearHistory()">Clear History</button>
        </div>
    `);
}

function clearHistory() {
    tabs.forEach(t => { t.history = []; t.historyIndex = -1; });
    showHistory();
}

function showDownloads() {
    toggleMenu();
    showModal('Downloads', `
        <div class="modal-body">
            <p style="color: #9aa0a6; margin-bottom: 15px;">Track your downloads here</p>
            ${downloads.length === 0 ? '<p style="color: #9aa0a6;">No downloads yet</p>' : 
                downloads.map((d, i) => `
                    <div class="list-item">
                        <div class="list-item-text">
                            <strong>${d.name}</strong><br>
                            <small style="color: #9aa0a6;">${d.url} - ${d.date}</small>
                        </div>
                        <div class="list-item-actions">
                            <button class="btn btn-danger" onclick="deleteDownload(${i})">Delete</button>
                        </div>
                    </div>
                `).join('')
            }
            <button class="btn btn-primary" onclick="addDownload()">Add Download</button>
        </div>
    `);
}

function addDownload() {
    const name = prompt('Download name:');
    const url = prompt('Download URL:');
    if (name && url) {
        downloads.push({ name, url, date: new Date().toLocaleString() });
        localStorage.setItem('blscDownloads', JSON.stringify(downloads));
        showDownloads();
    }
}

function deleteDownload(index) {
    downloads.splice(index, 1);
    localStorage.setItem('blscDownloads', JSON.stringify(downloads));
    showDownloads();
}

function showPasswords() {
    toggleMenu();
    showModal('Saved Passwords', `
        <div class="modal-body">
            <p style="color: #9aa0a6; margin-bottom: 15px;">Manage your saved passwords</p>
            ${passwords.length === 0 ? '<p style="color: #9aa0a6;">No passwords saved</p>' : 
                passwords.map((p, i) => `
                    <div class="list-item">
                        <div class="list-item-text">
                            <strong>${p.site}</strong><br>
                            <small style="color: #9aa0a6;">Username: ${p.username}</small>
                        </div>
                        <div class="list-item-actions">
                            <button class="btn btn-primary" onclick="showPassword(${i})">Show</button>
                            <button class="btn btn-danger" onclick="deletePassword(${i})">Delete</button>
                        </div>
                    </div>
                `).join('')
            }
            <button class="btn btn-primary" onclick="addPassword()">Add Password</button>
        </div>
    `);
}

function addPassword() {
    const site = prompt('Website:');
    const username = prompt('Username:');
    const password = prompt('Password:');
    if (site && username && password) {
        passwords.push({ site, username, password });
        localStorage.setItem('blscPasswords', JSON.stringify(passwords));
        showPasswords();
    }
}

function showPassword(index) {
    alert(`Password: ${passwords[index].password}`);
}

function deletePassword(index) {
    passwords.splice(index, 1);
    localStorage.setItem('blscPasswords', JSON.stringify(passwords));
    showPasswords();
}

function showSettings() {
    toggleMenu();
    showModal('Settings', `
        <div class="modal-body">
            <h3 style="margin-bottom: 15px;">Browser Settings</h3>
            <div class="form-group">
                <label class="form-label">Search Engine</label>
                <select class="form-input" id="searchEngine">
                    <option value="bing">Bing</option>
                    <option value="google">Google</option>
                    <option value="duckduckgo">DuckDuckGo</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Homepage</label>
                <input type="text" class="form-input" id="homepage" placeholder="https://example.com">
            </div>
            <button class="btn btn-primary" onclick="saveSettings()">Save Settings</button>
        </div>
    `);
}

function saveSettings() {
    alert('Settings saved!');
    closeModal();
}

function savePageOffline() {
    const url = document.getElementById('addressBar').value;
    if (!url) {
        alert('No page loaded to save!');
        return;
    }
    
    const frame = document.getElementById('browserFrame');
    const title = tabs[currentTab].title || 'Saved Page';
    
    try {
        // Try to get iframe content
        const frameDoc = frame.contentDocument || frame.contentWindow.document;
        const htmlContent = frameDoc.documentElement.outerHTML;
        
        // Save to localStorage
        const savedPage = {
            title: title,
            url: url,
            content: htmlContent,
            date: new Date().toLocaleString(),
            favicon: tabs[currentTab].favicon || '📄'
        };
        
        savedPages.push(savedPage);
        localStorage.setItem('blscSavedPages', JSON.stringify(savedPages));
        
        alert(`Page "${title}" saved for offline viewing!`);
    } catch (e) {
        // If cross-origin, fetch the page
        alert('Saving page... This may take a moment.');
        
        fetch(url)
            .then(response => response.text())
            .then(htmlContent => {
                const savedPage = {
                    title: title,
                    url: url,
                    content: htmlContent,
                    date: new Date().toLocaleString(),
                    favicon: tabs[currentTab].favicon || '📄'
                };
                
                savedPages.push(savedPage);
                localStorage.setItem('blscSavedPages', JSON.stringify(savedPages));
                
                alert(`Page "${title}" saved for offline viewing!`);
            })
            .catch(err => {
                alert('Could not save this page. The website blocks saving due to security policies.');
            });
    }
}

function showSavedPages() {
    toggleMenu();
    showModal('Saved Pages (Offline)', `
        <div class="modal-body">
            <p style="color: #9aa0a6; margin-bottom: 15px;">View saved pages offline</p>
            ${savedPages.length === 0 ? '<p style="color: #9aa0a6;">No saved pages yet. Click the 💾 button to save a page.</p>' : 
                savedPages.map((p, i) => `
                    <div class="list-item">
                        <div class="list-item-text" onclick="loadSavedPage(${i}); closeModal();" style="cursor: pointer;">
                            <strong>${p.title}</strong><br>
                            <small style="color: #9aa0a6;">${p.date}</small>
                        </div>
                        <div class="list-item-actions">
                            <button class="btn btn-primary" onclick="downloadSavedPage(${i})">Download</button>
                            <button class="btn btn-danger" onclick="deleteSavedPage(${i})">Delete</button>
                        </div>
                    </div>
                `).join('')
            }
            ${savedPages.length > 0 ? '<button class="btn btn-danger" onclick="clearSavedPages()" style="margin-top: 10px;">Clear All</button>' : ''}
        </div>
    `);
}

function loadSavedPage(index) {
    const page = savedPages[index];
    const frame = document.getElementById('browserFrame');
    const homePage = document.getElementById('homePage');
    const errorPage = document.getElementById('errorPage');
    const addressBar = document.getElementById('addressBar');
    
    homePage.style.display = 'none';
    errorPage.style.display = 'none';
    frame.style.display = 'block';
    
    // Load saved HTML content
    frame.srcdoc = page.content;
    addressBar.value = page.url + ' (Offline)';
    
    tabs[currentTab].title = page.title + ' (Offline)';
    tabs[currentTab].favicon = page.favicon;
    updateTabDisplay();
}

function downloadSavedPage(index) {
    const page = savedPages[index];
    const blob = new Blob([page.content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${page.title.replace(/[^a-z0-9]/gi, '_')}.html`;
    a.click();
    URL.revokeObjectURL(url);
    alert('Page downloaded!');
}

function deleteSavedPage(index) {
    if (confirm('Delete this saved page?')) {
        savedPages.splice(index, 1);
        localStorage.setItem('blscSavedPages', JSON.stringify(savedPages));
        showSavedPages();
    }
}

function clearSavedPages() {
    if (confirm('Delete all saved pages?')) {
        savedPages = [];
        localStorage.setItem('blscSavedPages', JSON.stringify(savedPages));
        showSavedPages();
    }
}

function clearAllData() {
    if (confirm('Clear all browser data? This cannot be undone!')) {
        localStorage.clear();
        bookmarks = [];
        passwords = [];
        downloads = [];
        quickLinks = [];
        savedPages = [];
        alert('All data cleared!');
        location.reload();
    }
}

function toggleFullscreen() {
    const browserContent = document.querySelector('.browser-content');
    
    if (!document.fullscreenElement) {
        if (browserContent.requestFullscreen) {
            browserContent.requestFullscreen();
        } else if (browserContent.webkitRequestFullscreen) {
            browserContent.webkitRequestFullscreen();
        } else if (browserContent.msRequestFullscreen) {
            browserContent.msRequestFullscreen();
        }
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }
}

function showModal(title, content) {
    const modal = document.getElementById('modal');
    modal.classList.add('active');
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                ${title}
                <button class="modal-close" onclick="closeModal()">×</button>
            </div>
            ${content}
        </div>
    `;
}

function closeModal() {
    document.getElementById('modal').classList.remove('active');
}

window.onclick = function(event) {
    const modal = document.getElementById('modal');
    if (event.target === modal) {
        closeModal();
    }
}

init();
