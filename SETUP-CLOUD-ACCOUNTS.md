# BLSC Cloud Account System Setup Guide

## 🌍 How It Works
Your users can now register and login from **ANYWHERE in the world** - just like Google accounts!

## 📋 Setup Steps (5 minutes)

### Step 1: Create JSONBin.io Account (FREE)
1. Go to https://jsonbin.io/
2. Click "Sign Up" (it's free!)
3. Verify your email

### Step 2: Create a Bin (Database)
1. After login, click "Create a Bin"
2. Paste this initial data:
```json
{
  "users": {}
}
```
3. Click "Create"
4. Copy the **Bin ID** from the URL (looks like: `67890abcdef123456789`)

### Step 3: Get Your API Key
1. Click on your profile icon (top right)
2. Go to "API Keys"
3. Copy your **X-Access-Key**

### Step 4: Update blsc-account.js
Open `blsc-account.js` and replace these lines at the top:

```javascript
JSONBIN_API_KEY: '$2a$10$YOUR_ACTUAL_API_KEY_HERE',
JSONBIN_BIN_ID: 'YOUR_ACTUAL_BIN_ID_HERE',
```

### Step 5: Deploy to Vercel
1. Push your code to GitHub
2. Go to https://vercel.com/
3. Import your GitHub repository
4. Deploy!

## ✅ That's It!
Now anyone can:
- Register from any device/location
- Login from any device/location
- Their account works everywhere!

Admin panel: `admin-users.html`

## 🔒 Security Notes
- For production, consider using Firebase Auth (more secure)
- The current system stores passwords in plain text (for demo)
- JSONBin.io free tier: 10,000 requests/month

## 🆘 Need Help?
- JSONBin.io Docs: https://jsonbin.io/api-reference
- Firebase (alternative): https://firebase.google.com/

## 📁 User Data Structure
Each user is stored like this:
```json
{
  "user@email.com": {
    "id": "user_1234567890",
    "name": "John Doe",
    "email": "user@email.com",
    "password": "userpassword",
    "folder": "useraccountssave/john_doe_1234567890",
    "createdAt": "2024-12-24T10:00:00.000Z",
    "lastLogin": "2024-12-24T10:00:00.000Z"
  }
}
```
