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
