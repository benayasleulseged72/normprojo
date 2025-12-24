/**
 * BLSC Account Management System - Firebase Version
 * Real database storage - works from anywhere!
 * by Benayas Leulseged - Dec 2024
 * 
 * SETUP INSTRUCTIONS:
 * 1. Go to https://console.firebase.google.com/
 * 2. Create a new project (free)
 * 3. Go to Build > Firestore Database > Create database
 * 4. Choose "Start in test mode" for now
 * 5. Go to Project Settings > General > Your apps > Web app
 * 6. Copy your config and replace the firebaseConfig below
 */

// Firebase Configuration - REPLACE WITH YOUR OWN!
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
};

// Initialize Firebase (load these scripts in your HTML first)
// <script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js"></script>
// <script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore-compat.js"></script>
// <script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-auth-compat.js"></script>

let db = null;
let auth = null;

function initFirebase() {
    if (typeof firebase !== 'undefined' && !firebase.apps.length) {
        firebase.initializeApp(firebaseConfig);
        db = firebase.firestore();
        auth = firebase.auth();
        console.log('✅ Firebase initialized');
    }
}

const BLSC_ACCOUNT = {
    SESSION_KEY: 'blsc_session',
    
    // Initialize
    init() {
        initFirebase();
    },
    
    // Get current session from localStorage (for quick access)
    getSession() {
        const session = localStorage.getItem(this.SESSION_KEY);
        return session ? JSON.parse(session) : null;
    },
    
    // Check if user is logged in
    isLoggedIn() {
        return this.getSession() !== null;
    },
    
    // Get current user data
    async getCurrentUser() {
        const session = this.getSession();
        if (!session) return null;
        
        try {
            const doc = await db.collection('users').doc(session.odId).get();
            if (doc.exists) {
                return { id: doc.id, ...doc.data() };
            }
        } catch (error) {
            console.error('Error getting user:', error);
        }
        return null;
    },
    
    // Register new user - saves to Firebase (accessible from anywhere!)
    async signup(name, email, password) {
        if (!db) {
            initFirebase();
            if (!db) return { success: false, message: 'Database not initialized. Check Firebase config.' };
        }
        
        try {
            // Check if email already exists
            const existing = await db.collection('users').where('email', '==', email).get();
            if (!existing.empty) {
                return { success: false, message: 'Email already registered' };
            }
            
            // Create folder name from user's name
            const odId = Date.now().toString();
            const folderName = name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '') + '_' + odId;
            
            // Create user document in Firebase
            const userData = {
                name: name,
                email: email,
                password: password, // In production, use Firebase Auth instead!
                avatar: null,
                createdAt: new Date().toISOString(),
                folder: 'useraccountssave/' + folderName,
                lastLogin: new Date().toISOString()
            };
            
            await db.collection('users').doc(odId).set(userData);
            
            // Create session
            this.createSession({ odId, ...userData });
            
            return { success: true, message: 'Account created successfully!', user: userData };
            
        } catch (error) {
            console.error('Signup error:', error);
            return { success: false, message: 'Error creating account: ' + error.message };
        }
    },
    
    // Login user - checks Firebase database
    async login(email, password, remember = false) {
        if (!db) {
            initFirebase();
            if (!db) return { success: false, message: 'Database not initialized' };
        }
        
        try {
            // Find user by email
            const snapshot = await db.collection('users').where('email', '==', email).get();
            
            if (snapshot.empty) {
                return { success: false, message: 'Email not found' };
            }
            
            const doc = snapshot.docs[0];
            const user = doc.data();
            
            if (user.password !== password) {
                return { success: false, message: 'Incorrect password' };
            }
            
            // Update last login
            await db.collection('users').doc(doc.id).update({
                lastLogin: new Date().toISOString()
            });
            
            // Create session
            this.createSession({ odId: doc.id, ...user }, remember);
            
            return { success: true, message: 'Login successful!', user };
            
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: 'Error logging in: ' + error.message };
        }
    },
    
    // Create session
    createSession(user, remember = false) {
        const session = {
            odId: user.odId,
            email: user.email,
            name: user.name,
            folder: user.folder,
            loginTime: new Date().toISOString(),
            remember: remember
        };
        localStorage.setItem(this.SESSION_KEY, JSON.stringify(session));
    },
    
    // Logout user
    logout() {
        localStorage.removeItem(this.SESSION_KEY);
        window.location.reload();
    },
    
    // Get all users (admin function)
    async getAllUsers() {
        if (!db) return [];
        try {
            const snapshot = await db.collection('users').get();
            return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        } catch (error) {
            console.error('Error getting users:', error);
            return [];
        }
    },
    
    // Get user initials for avatar
    getInitials(name) {
        if (!name) return '?';
        const parts = name.trim().split(' ');
        if (parts.length >= 2) {
            return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    },
    
    // Generate avatar color based on name
    getAvatarColor(name) {
        const colors = ['#3fb950', '#58a6ff', '#8b5cf6', '#f97316', '#ec4899', '#14b8a6', '#eab308'];
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        return colors[Math.abs(hash) % colors.length];
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    BLSC_ACCOUNT.init();
});
