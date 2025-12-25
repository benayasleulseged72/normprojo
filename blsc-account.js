/**
 * BLSC Account Management System
 * Cloud-based storage using JSONBin.io (FREE!)
 * Users can register/login from ANYWHERE in the world!
 * by Benayas Leulseged - Dec 2024
 */

const BLSC_ACCOUNT = {
    // JSONBin.io Configuration
    JSONBIN_API_KEY: '$2a$10$jaYV5knIHoiKLb.lj7qAK.K/hiX5So2LTUA3L6Vk6IvBHY7E6os4S',
    JSONBIN_BIN_ID: '694c5a5bae596e708faf0517',
    
    // Local session key
    SESSION_KEY: 'blsc_session',
    
    // Cache for users
    _usersCache: null,
    _cacheTime: null,
    
    // Get all users from cloud
    async getUsers() {
        if (this._usersCache && this._cacheTime && (Date.now() - this._cacheTime < 30000)) {
            return this._usersCache;
        }
        
        try {
            const response = await fetch(`https://api.jsonbin.io/v3/b/${this.JSONBIN_BIN_ID}/latest`, {
                headers: { 'X-Access-Key': this.JSONBIN_API_KEY }
            });
            
            if (response.ok) {
                const data = await response.json();
                this._usersCache = data.record.users || {};
                this._cacheTime = Date.now();
                return this._usersCache;
            }
        } catch (error) {
            console.error('Error fetching users:', error);
        }
        return {};
    },
    
    // Save users to cloud
    async saveUsers(users) {
        try {
            const response = await fetch(`https://api.jsonbin.io/v3/b/${this.JSONBIN_BIN_ID}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Access-Key': this.JSONBIN_API_KEY
                },
                body: JSON.stringify({ users: users })
            });
            
            if (response.ok) {
                this._usersCache = users;
                this._cacheTime = Date.now();
                return true;
            }
        } catch (error) {
            console.error('Error saving users:', error);
        }
        return false;
    },

    // Get current session
    getSession() {
        const session = localStorage.getItem(this.SESSION_KEY);
        return session ? JSON.parse(session) : null;
    },
    
    isLoggedIn() {
        return this.getSession() !== null;
    },
    
    getCurrentUser() {
        const session = this.getSession();
        if (!session) return null;
        return session.user || null;
    },
    
    // Register new user
    async signup(name, email, password) {
        try {
            const users = await this.getUsers();
            
            if (users[email]) {
                return { success: false, message: 'Email already registered' };
            }
            
            const userId = 'user_' + Date.now();
            const folderName = name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '') + '_' + userId.split('_')[1];
            
            const user = {
                id: userId,
                name: name,
                email: email,
                password: password,
                avatar: null,
                createdAt: new Date().toISOString(),
                folder: 'useraccountssave/' + folderName,
                lastLogin: new Date().toISOString()
            };
            
            users[email] = user;
            
            const saved = await this.saveUsers(users);
            if (!saved) {
                return { success: false, message: 'Error saving to cloud. Please try again.' };
            }
            
            this.createSession(user);
            return { success: true, message: 'Account created successfully!', user };
            
        } catch (error) {
            console.error('Signup error:', error);
            return { success: false, message: 'Error: ' + error.message };
        }
    },
    
    // Login user
    async login(email, password, remember = false) {
        try {
            const users = await this.getUsers();
            const user = users[email];
            
            if (!user) {
                return { success: false, message: 'Email not found' };
            }
            
            if (user.password !== password) {
                return { success: false, message: 'Incorrect password' };
            }
            
            user.lastLogin = new Date().toISOString();
            users[email] = user;
            await this.saveUsers(users);
            
            this.createSession(user, remember);
            return { success: true, message: 'Login successful!', user };
            
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: 'Error: ' + error.message };
        }
    },

    createSession(user, remember = false) {
        const session = {
            user: user,
            email: user.email,
            name: user.name,
            loginTime: new Date().toISOString(),
            remember: remember
        };
        localStorage.setItem(this.SESSION_KEY, JSON.stringify(session));
    },
    
    logout() {
        localStorage.removeItem(this.SESSION_KEY);
        window.location.reload();
    },
    
    getInitials(name) {
        if (!name) return '?';
        const parts = name.trim().split(' ');
        if (parts.length >= 2) {
            return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    },
    
    getAvatarColor(name) {
        const colors = ['#3fb950', '#58a6ff', '#8b5cf6', '#f97316', '#ec4899', '#14b8a6', '#eab308'];
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        return colors[Math.abs(hash) % colors.length];
    },
    
    // ========== SUBSCRIPTION MANAGEMENT (CLOUD) ==========
    
    // Get user's subscription for a service
    async getSubscription(service) {
        if (!this.isLoggedIn()) return null;
        const user = this.getCurrentUser();
        const users = await this.getUsers();
        const userData = users[user.email];
        if (!userData || !userData.subscriptions) return null;
        return userData.subscriptions[service] || null;
    },
    
    // Check if user has active subscription
    async hasActiveSubscription(service) {
        const sub = await this.getSubscription(service);
        if (!sub) return false;
        if (sub.type === 'unlimited') return true;
        return new Date() < new Date(sub.endDate);
    },
    
    // Activate free trial (30 days) - saves to CLOUD
    async activateTrial(service) {
        if (!this.isLoggedIn()) {
            return { success: false, message: 'Please login first' };
        }
        
        const user = this.getCurrentUser();
        const users = await this.getUsers();
        const userData = users[user.email];
        
        if (!userData) {
            return { success: false, message: 'User not found' };
        }
        
        // Initialize subscriptions if not exists
        if (!userData.subscriptions) {
            userData.subscriptions = {};
        }
        
        // Check if already has subscription for this service
        const existing = userData.subscriptions[service];
        if (existing) {
            if (existing.type === 'unlimited') {
                return { success: true, message: 'You have unlimited access!', active: true };
            }
            if (new Date() < new Date(existing.endDate)) {
                const daysLeft = Math.ceil((new Date(existing.endDate) - new Date()) / (1000*60*60*24));
                return { success: true, message: 'Active! ' + daysLeft + ' days left', active: true, daysLeft: daysLeft };
            }
            // Expired
            return { success: false, message: 'Your subscription has expired', expired: true };
        }
        
        // Create new 30-day trial
        const startDate = new Date();
        const endDate = new Date();
        endDate.setDate(endDate.getDate() + 30);
        
        userData.subscriptions[service] = {
            type: 'free_trial',
            service: service,
            startDate: startDate.toISOString(),
            endDate: endDate.toISOString(),
            activatedAt: startDate.toISOString()
        };
        
        users[user.email] = userData;
        const saved = await this.saveUsers(users);
        
        if (saved) {
            // Update local session
            this.createSession(userData);
            return { success: true, message: '30-day trial activated!', endDate: endDate.toLocaleDateString() };
        }
        return { success: false, message: 'Error saving. Try again.' };
    },
    
    // Activate paid subscription (admin use)
    async activateSubscription(email, service, type, days) {
        const users = await this.getUsers();
        const userData = users[email];
        
        if (!userData) {
            return { success: false, message: 'User not found' };
        }
        
        if (!userData.subscriptions) {
            userData.subscriptions = {};
        }
        
        const startDate = new Date();
        let endDate = null;
        
        if (type !== 'unlimited') {
            endDate = new Date();
            endDate.setDate(endDate.getDate() + days);
        }
        
        userData.subscriptions[service] = {
            type: type,
            service: service,
            startDate: startDate.toISOString(),
            endDate: endDate ? endDate.toISOString() : null,
            activatedAt: startDate.toISOString()
        };
        
        users[email] = userData;
        return await this.saveUsers(users);
    }
};

// Account Dropdown UI
function createAccountDropdown() {
    const user = BLSC_ACCOUNT.getCurrentUser();
    const isLoggedIn = BLSC_ACCOUNT.isLoggedIn();
    
    const userIcon = document.querySelector('.user-icon');
    if (!userIcon) return;
    
    let basePath = '';
    const existingHref = userIcon.getAttribute('href') || '';
    if (existingHref.includes('auth.html')) {
        basePath = existingHref.replace('auth.html', '');
    }
    
    const existingImg = userIcon.querySelector('img');
    let userImgPath = basePath + 'user.png';
    if (existingImg && existingImg.src) userImgPath = existingImg.src;
    
    const dropdownContainer = document.createElement('div');
    dropdownContainer.className = 'account-dropdown-container';
    dropdownContainer.style.cssText = 'position:relative;display:inline-block;margin-left:15px;';
    
    const trigger = document.createElement('button');
    trigger.className = 'account-trigger';
    trigger.type = 'button';
    
    if (isLoggedIn && user) {
        const initials = BLSC_ACCOUNT.getInitials(user.name);
        const color = BLSC_ACCOUNT.getAvatarColor(user.name);
        trigger.innerHTML = `<div style="width:40px;height:40px;border-radius:50%;background:${color};display:flex;align-items:center;justify-content:center;color:#fff;font-weight:600;font-size:14px;">${initials}</div>`;
    } else {
        trigger.innerHTML = `<img src="${userImgPath}" alt="User" style="width:40px;height:40px;border-radius:12px;">`;
    }
    trigger.style.cssText = 'background:none;border:none;cursor:pointer;padding:4px;border-radius:50%;transition:all 0.3s;';
    
    const dropdown = document.createElement('div');
    dropdown.className = 'account-dropdown';
    dropdown.style.cssText = 'position:absolute;top:calc(100% + 10px);right:0;width:320px;background:#1a1a1a;border:1px solid rgba(255,255,255,0.1);border-radius:16px;box-shadow:0 10px 40px rgba(0,0,0,0.5);opacity:0;visibility:hidden;transform:translateY(-10px);transition:all 0.3s;z-index:1000;overflow:hidden;';

    if (isLoggedIn && user) {
        const initials = BLSC_ACCOUNT.getInitials(user.name);
        const color = BLSC_ACCOUNT.getAvatarColor(user.name);
        dropdown.innerHTML = `
            <div style="padding:20px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.1);">
                <div style="width:70px;height:70px;border-radius:50%;background:${color};display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:24px;margin:0 auto 12px;">${initials}</div>
                <div style="font-size:16px;font-weight:600;color:#fff;margin-bottom:4px;">${user.name}</div>
                <div style="font-size:13px;color:rgba(255,255,255,0.5);">${user.email}</div>
            </div>
            <div style="padding:8px;">
                <a href="${basePath}auth.html" class="dropdown-item" style="display:flex;align-items:center;gap:12px;padding:12px 16px;color:rgba(255,255,255,0.8);text-decoration:none;border-radius:10px;">Manage Account</a>
                <a href="#" class="dropdown-item" onclick="BLSC_ACCOUNT.logout();return false;" style="display:flex;align-items:center;gap:12px;padding:12px 16px;color:#f87171;text-decoration:none;border-radius:10px;">Sign Out</a>
            </div>
            <div style="padding:12px 20px;background:rgba(255,255,255,0.02);border-top:1px solid rgba(255,255,255,0.1);text-align:center;">
                <span style="font-size:12px;color:rgba(255,255,255,0.4);">BLSC Account • Cloud ☁️</span>
            </div>`;
    } else {
        dropdown.innerHTML = `
            <div style="padding:24px;text-align:center;">
                <div style="width:60px;height:60px;border-radius:50%;background:rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;margin:0 auto 16px;">👤</div>
                <div style="font-size:16px;font-weight:600;color:#fff;margin-bottom:8px;">Welcome to BLSC</div>
                <div style="font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:20px;">Sign in to access all features</div>
                <a href="${basePath}auth.html" style="display:block;padding:14px;background:linear-gradient(135deg,#3fb950,#2ea043);color:#fff;text-decoration:none;border-radius:12px;font-weight:600;">Sign In</a>
            </div>`;
    }
    
    userIcon.parentNode.replaceChild(dropdownContainer, userIcon);
    dropdownContainer.appendChild(trigger);
    dropdownContainer.appendChild(dropdown);
    
    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = dropdown.style.opacity === '1';
        dropdown.style.opacity = isOpen ? '0' : '1';
        dropdown.style.visibility = isOpen ? 'hidden' : 'visible';
        dropdown.style.transform = isOpen ? 'translateY(-10px)' : 'translateY(0)';
    });
    
    document.addEventListener('click', () => {
        dropdown.style.opacity = '0';
        dropdown.style.visibility = 'hidden';
        dropdown.style.transform = 'translateY(-10px)';
    });
}

document.addEventListener('DOMContentLoaded', createAccountDropdown);

// ========== BANNED USER CHECK ==========
// Shows hacker-style BANNED screen if user is banned
async function checkIfBanned() {
    if (!BLSC_ACCOUNT.isLoggedIn()) return false;
    
    const user = BLSC_ACCOUNT.getCurrentUser();
    if (!user) return false;
    
    try {
        const users = await BLSC_ACCOUNT.getUsers();
        const userData = users[user.email];
        
        if (userData && userData.banned) {
            showBannedScreen(userData);
            return true;
        }
    } catch (e) {
        console.error('Ban check error:', e);
    }
    return false;
}

function showBannedScreen(userData) {
    // Create fullscreen hacker-style banned overlay
    const overlay = document.createElement('div');
    overlay.id = 'banned-overlay';
    overlay.innerHTML = `
        <style>
            #banned-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: #000;
                z-index: 999999;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
                font-family: 'Courier New', monospace;
                overflow: hidden;
            }
            #banned-overlay::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: repeating-linear-gradient(
                    0deg,
                    rgba(0, 255, 0, 0.03) 0px,
                    rgba(0, 255, 0, 0.03) 1px,
                    transparent 1px,
                    transparent 2px
                );
                pointer-events: none;
                animation: scanlines 0.1s linear infinite;
            }
            @keyframes scanlines {
                0% { transform: translateY(0); }
                100% { transform: translateY(2px); }
            }
            @keyframes glitch {
                0%, 100% { transform: translate(0); }
                20% { transform: translate(-2px, 2px); }
                40% { transform: translate(-2px, -2px); }
                60% { transform: translate(2px, 2px); }
                80% { transform: translate(2px, -2px); }
            }
            @keyframes flicker {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.8; }
                75% { opacity: 0.9; }
            }
            @keyframes typing {
                from { width: 0; }
                to { width: 100%; }
            }
            .banned-title {
                font-size: clamp(60px, 15vw, 150px);
                font-weight: bold;
                color: #ff0000;
                text-shadow: 
                    0 0 10px #ff0000,
                    0 0 20px #ff0000,
                    0 0 40px #ff0000,
                    0 0 80px #ff0000,
                    4px 4px 0 #000,
                    -4px -4px 0 #000;
                animation: glitch 0.3s infinite, flicker 0.5s infinite;
                letter-spacing: 20px;
                margin-bottom: 30px;
            }
            .banned-skull {
                font-size: 100px;
                animation: glitch 0.5s infinite;
                margin-bottom: 20px;
            }
            .banned-info {
                color: #00ff00;
                font-size: 16px;
                text-align: center;
                max-width: 600px;
                line-height: 1.8;
                text-shadow: 0 0 10px #00ff00;
            }
            .banned-info .label {
                color: #ff0000;
                font-weight: bold;
            }
            .banned-reason {
                margin-top: 30px;
                padding: 20px;
                border: 2px solid #ff0000;
                background: rgba(255, 0, 0, 0.1);
                color: #ff0000;
                font-size: 18px;
                animation: flicker 1s infinite;
            }
            .banned-code {
                margin-top: 40px;
                color: #00ff00;
                font-size: 12px;
                opacity: 0.7;
            }
            .matrix-bg {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                overflow: hidden;
                opacity: 0.1;
                pointer-events: none;
            }
            .matrix-char {
                position: absolute;
                color: #00ff00;
                font-size: 14px;
                animation: fall linear infinite;
            }
            @keyframes fall {
                0% { transform: translateY(-100vh); opacity: 1; }
                100% { transform: translateY(100vh); opacity: 0; }
            }
        </style>
        <div class="matrix-bg" id="matrix"></div>
        <div class="banned-skull">💀</div>
        <div class="banned-title">BANNED</div>
        <div class="banned-info">
            <p><span class="label">USER:</span> ${userData.email}</p>
            <p><span class="label">STATUS:</span> PERMANENTLY BLOCKED</p>
            <p><span class="label">DATE:</span> ${userData.bannedAt ? new Date(userData.bannedAt).toLocaleString() : 'Unknown'}</p>
        </div>
        <div class="banned-reason">
            ⚠️ REASON: ${userData.banReason || 'Violation of Terms of Service'}
        </div>
        <div class="banned-code">
            [ACCESS_DENIED] [ERROR_CODE: 0x8007045D] [SYSTEM_LOCKOUT]<br>
            Your account has been terminated. All services revoked.<br>
            Contact support if you believe this is an error.
        </div>
    `;
    
    document.body.innerHTML = '';
    document.body.appendChild(overlay);
    
    // Add matrix rain effect
    const matrix = document.getElementById('matrix');
    const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
    for (let i = 0; i < 50; i++) {
        const char = document.createElement('div');
        char.className = 'matrix-char';
        char.style.left = Math.random() * 100 + 'vw';
        char.style.animationDuration = (Math.random() * 3 + 2) + 's';
        char.style.animationDelay = Math.random() * 5 + 's';
        char.textContent = chars[Math.floor(Math.random() * chars.length)];
        matrix.appendChild(char);
    }
    
    // Clear session
    localStorage.removeItem(BLSC_ACCOUNT.SESSION_KEY);
}

// Auto-check on page load
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(checkIfBanned, 500);
    createSystemStatusIndicator();
});

// ========== SYSTEM ONLINE STATUS INDICATOR ==========
function createSystemStatusIndicator() {
    // Create floating status indicator
    const indicator = document.createElement('div');
    indicator.id = 'blsc-system-status';
    indicator.innerHTML = `
        <style>
            #blsc-system-status {
                position: fixed;
                bottom: 20px;
                right: 20px;
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 10px 16px;
                background: rgba(10, 10, 10, 0.9);
                border: 1px solid rgba(63, 185, 80, 0.3);
                border-radius: 100px;
                font-family: 'Inter', sans-serif;
                font-size: 12px;
                color: #fff;
                z-index: 9998;
                backdrop-filter: blur(10px);
                transition: all 0.3s;
                cursor: pointer;
            }
            #blsc-system-status:hover {
                transform: scale(1.05);
            }
            #blsc-system-status.offline {
                border-color: rgba(239, 68, 68, 0.3);
            }
            #blsc-system-status .dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #3fb950;
                animation: statusPulse 2s infinite;
            }
            #blsc-system-status.offline .dot {
                background: #ef4444;
            }
            @keyframes statusPulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.4; }
            }
            #blsc-system-status .text {
                color: #3fb950;
                font-weight: 600;
            }
            #blsc-system-status.offline .text {
                color: #ef4444;
            }
        </style>
        <div class="dot"></div>
        <span class="text">System Online</span>
    `;
    document.body.appendChild(indicator);
    
    // Check system status
    checkCloudStatus();
    setInterval(checkCloudStatus, 60000); // Check every minute
}

async function checkCloudStatus() {
    const indicator = document.getElementById('blsc-system-status');
    if (!indicator) return;
    
    try {
        const response = await fetch(`https://api.jsonbin.io/v3/b/${BLSC_ACCOUNT.JSONBIN_BIN_ID}/latest`, {
            headers: { 'X-Access-Key': BLSC_ACCOUNT.JSONBIN_API_KEY }
        });
        
        if (response.ok) {
            indicator.classList.remove('offline');
            indicator.querySelector('.text').textContent = 'System Online';
        } else {
            indicator.classList.add('offline');
            indicator.querySelector('.text').textContent = 'System Offline';
        }
    } catch (error) {
        indicator.classList.add('offline');
        indicator.querySelector('.text').textContent = 'System Offline';
    }
}
