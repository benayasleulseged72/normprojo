/**
 * BLSC Account Management System
 * Cloud-based storage using Firebase Realtime Database (FREE - Unlimited!)
 * Users can register/login from ANYWHERE in the world!
 * by Benayas Leulseged - Dec 2024
 */

// Firebase Configuration
const FIREBASE_CONFIG = {
    apiKey: "AIzaSyDMBjv-q88GRnJi6Dnr-1ltlj3Fu2P3tys",
    authDomain: "blsc-accounts-206b9.firebaseapp.com",
    databaseURL: "https://blsc-accounts-206b9-default-rtdb.firebaseio.com",
    projectId: "blsc-accounts-206b9",
    storageBucket: "blsc-accounts-206b9.firebasestorage.app",
    messagingSenderId: "959298538562",
    appId: "1:959298538562:web:752354d8da2851d65db1db"
};

const FIREBASE_DB_URL = FIREBASE_CONFIG.databaseURL;

const BLSC_ACCOUNT = {
    // Local session key
    SESSION_KEY: 'blsc_session',
    
    // Cache for users
    _usersCache: null,
    _cacheTime: null,
    
    // Get all users from Firebase
    async getUsers() {
        if (this._usersCache && this._cacheTime && (Date.now() - this._cacheTime < 10000)) {
            return this._usersCache;
        }
        
        try {
            const response = await fetch(`${FIREBASE_DB_URL}/users.json`);
            if (response.ok) {
                const data = await response.json();
                this._usersCache = data || {};
                this._cacheTime = Date.now();
                return this._usersCache;
            }
        } catch (error) {
            console.error('Error fetching users:', error);
        }
        return this._usersCache || {};
    },
    
    // Save all users to Firebase
    async saveUsers(users) {
        try {
            const response = await fetch(`${FIREBASE_DB_URL}/users.json`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(users)
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
    async signup(name, email, password, phone = '') {
        try {
            const users = await this.getUsers();
            const emailKey = email.replace(/\./g, '_'); // Firebase doesn't allow dots in keys
            
            if (users[emailKey]) {
                return { success: false, message: 'Email already registered' };
            }
            
            const userId = 'user_' + Date.now();
            const user = {
                id: userId,
                name: name,
                email: email,
                phone: phone,
                password: password,
                avatar: null,
                createdAt: new Date().toISOString(),
                lastLogin: new Date().toISOString()
            };
            
            users[emailKey] = user;
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
            const emailKey = email.replace(/\./g, '_');
            const user = users[emailKey];
            
            if (!user) {
                return { success: false, message: 'Email not found' };
            }
            
            if (user.password !== password) {
                return { success: false, message: 'Incorrect password' };
            }
            
            user.lastLogin = new Date().toISOString();
            users[emailKey] = user;
            await this.saveUsers(users);
            
            this.createSession(user, remember);
            return { success: true, message: 'Login successful!', user };
            
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: 'Error: ' + error.message };
        }
    },

    // Social Login (Google, GitHub, etc.)
    async socialLogin(provider, email, name) {
        try {
            const users = await this.getUsers();
            const emailKey = email.replace(/\./g, '_');
            let user = users[emailKey];
            
            if (user) {
                user.lastLogin = new Date().toISOString();
                user.provider = provider;
                users[emailKey] = user;
                await this.saveUsers(users);
                this.createSession(user, true);
                return { success: true, message: 'Welcome back!', user };
            } else {
                const userId = 'user_' + Date.now();
                user = {
                    id: userId,
                    name: name,
                    email: email,
                    password: null,
                    provider: provider,
                    avatar: null,
                    createdAt: new Date().toISOString(),
                    lastLogin: new Date().toISOString()
                };
                
                users[emailKey] = user;
                const saved = await this.saveUsers(users);
                
                if (!saved) {
                    return { success: false, message: 'Error saving to cloud.' };
                }
                
                this.createSession(user, true);
                return { success: true, message: 'Account created!', user };
            }
        } catch (error) {
            console.error('Social login error:', error);
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

    // ========== SUBSCRIPTION MANAGEMENT ==========
    
    async getSubscription(service) {
        if (!this.isLoggedIn()) return null;
        const user = this.getCurrentUser();
        const users = await this.getUsers();
        const emailKey = user.email.replace(/\./g, '_');
        const userData = users[emailKey];
        if (!userData || !userData.subscriptions) return null;
        return userData.subscriptions[service] || null;
    },
    
    async hasActiveSubscription(service) {
        const sub = await this.getSubscription(service);
        if (!sub) return false;
        if (sub.type === 'unlimited') return true;
        return new Date() < new Date(sub.endDate);
    },
    
    async activateTrial(service) {
        if (!this.isLoggedIn()) {
            return { success: false, message: 'Please login first' };
        }
        
        const user = this.getCurrentUser();
        const users = await this.getUsers();
        const emailKey = user.email.replace(/\./g, '_');
        const userData = users[emailKey];
        
        if (!userData) {
            return { success: false, message: 'User not found' };
        }
        
        if (!userData.subscriptions) {
            userData.subscriptions = {};
        }
        
        const existing = userData.subscriptions[service];
        if (existing) {
            if (existing.type === 'unlimited') {
                return { success: true, message: 'You have unlimited access!', active: true };
            }
            if (new Date() < new Date(existing.endDate)) {
                const daysLeft = Math.ceil((new Date(existing.endDate) - new Date()) / (1000*60*60*24));
                return { success: true, message: 'Active! ' + daysLeft + ' days left', active: true, daysLeft: daysLeft };
            }
            return { success: false, message: 'Your subscription has expired', expired: true };
        }
        
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
        
        users[emailKey] = userData;
        const saved = await this.saveUsers(users);
        
        if (saved) {
            this.createSession(userData);
            return { success: true, message: '30-day trial activated!', endDate: endDate.toLocaleDateString() };
        }
        return { success: false, message: 'Error saving. Try again.' };
    },
    
    async activateSubscription(email, service, type, days) {
        const users = await this.getUsers();
        const emailKey = email.replace(/\./g, '_');
        const userData = users[emailKey];
        
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
        
        users[emailKey] = userData;
        return await this.saveUsers(users);
    },
    
    // ========== COURSE ENROLLMENT ==========
    
    async isEnrolledInCourse(courseId) {
        if (!this.isLoggedIn()) return false;
        const user = this.getCurrentUser();
        const users = await this.getUsers();
        const emailKey = user.email.replace(/\./g, '_');
        const userData = users[emailKey];
        if (!userData || !userData.courses) return false;
        return userData.courses[courseId]?.enrolled === true;
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
        trigger.innerHTML = `<img src="${basePath}user.png" alt="User" style="width:40px;height:40px;border-radius:12px;" onerror="this.outerHTML='👤'">`;
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
                <a href="${basePath}auth.html" style="display:flex;align-items:center;gap:12px;padding:12px 16px;color:rgba(255,255,255,0.8);text-decoration:none;border-radius:10px;">Manage Account</a>
                <a href="#" onclick="BLSC_ACCOUNT.logout();return false;" style="display:flex;align-items:center;gap:12px;padding:12px 16px;color:#f87171;text-decoration:none;border-radius:10px;">Sign Out</a>
            </div>
            <div style="padding:12px 20px;background:rgba(255,255,255,0.02);border-top:1px solid rgba(255,255,255,0.1);text-align:center;">
                <span style="font-size:12px;color:rgba(255,255,255,0.4);">BLSC Account • Firebase ☁️</span>
            </div>`;
    } else {
        dropdown.innerHTML = `
            <div style="padding:24px;text-align:center;">
                <div style="width:60px;height:60px;border-radius:50%;background:rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;margin:0 auto 16px;font-size:30px;">👤</div>
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
async function checkIfBanned() {
    if (!BLSC_ACCOUNT.isLoggedIn()) return false;
    
    const user = BLSC_ACCOUNT.getCurrentUser();
    if (!user) return false;
    
    try {
        const users = await BLSC_ACCOUNT.getUsers();
        const emailKey = user.email.replace(/\./g, '_');
        const userData = users[emailKey];
        
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
    const overlay = document.createElement('div');
    overlay.id = 'banned-overlay';
    overlay.innerHTML = `
        <style>
            #banned-overlay{position:fixed;top:0;left:0;width:100vw;height:100vh;background:#000;z-index:999999;display:flex;align-items:center;justify-content:center;flex-direction:column;font-family:'Courier New',monospace}
            .banned-title{font-size:100px;font-weight:bold;color:#ff0000;text-shadow:0 0 20px #ff0000;animation:glitch 0.3s infinite}
            @keyframes glitch{0%,100%{transform:translate(0)}50%{transform:translate(-3px,3px)}}
            .banned-info{color:#0f0;font-size:16px;text-align:center;margin-top:30px}
            .banned-reason{margin-top:20px;padding:20px;border:2px solid #ff0000;color:#ff0000;font-size:18px}
        </style>
        <div style="font-size:80px;margin-bottom:20px">💀</div>
        <div class="banned-title">BANNED</div>
        <div class="banned-info">
            <p>USER: ${userData.email}</p>
            <p>STATUS: PERMANENTLY BLOCKED</p>
        </div>
        <div class="banned-reason">⚠️ ${userData.banReason || 'Violation of Terms of Service'}</div>
    `;
    
    document.body.innerHTML = '';
    document.body.appendChild(overlay);
    localStorage.removeItem(BLSC_ACCOUNT.SESSION_KEY);
}

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(checkIfBanned, 500);
    // Check ban status every 3 seconds - instant ban effect!
    setInterval(async () => {
        if (BLSC_ACCOUNT.isLoggedIn()) {
            BLSC_ACCOUNT._usersCache = null;
            BLSC_ACCOUNT._cacheTime = null;
            await checkIfBanned();
        }
    }, 3000);
});

// ========== BLSC VIDEOS (Firebase) ==========
const BLSC_VIDEOS = {
    _videosCache: null,
    _cacheTime: null,
    
    async getVideos() {
        if (this._videosCache && this._cacheTime && (Date.now() - this._cacheTime < 5000)) {
            return this._videosCache;
        }
        
        try {
            const response = await fetch(`${FIREBASE_DB_URL}/videos.json`);
            if (response.ok) {
                const data = await response.json();
                this._videosCache = data || [];
                this._cacheTime = Date.now();
                return this._videosCache;
            }
        } catch (error) {
            console.error('Error fetching videos:', error);
        }
        return [];
    },
    
    async saveVideos(videos) {
        try {
            const response = await fetch(`${FIREBASE_DB_URL}/videos.json`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(videos)
            });
            
            if (response.ok) {
                this._videosCache = videos;
                this._cacheTime = Date.now();
                return true;
            }
        } catch (error) {
            console.error('Error saving videos:', error);
        }
        return false;
    },
    
    clearCache() {
        this._videosCache = null;
        this._cacheTime = null;
    }
};
