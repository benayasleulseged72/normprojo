# Firebase Authentication Setup Guide

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Enter project name (e.g., "BLSC-Auth")
4. Disable Google Analytics (optional)
5. Click "Create project"

## Step 2: Enable Authentication Providers

1. In Firebase Console, go to **Build > Authentication**
2. Click **Get started**
3. Go to **Sign-in method** tab

### Enable Google:
1. Click on "Google"
2. Toggle "Enable"
3. Select your support email
4. Click "Save"

### Enable GitHub:
1. Click on "GitHub"
2. Toggle "Enable"
3. You need to create a GitHub OAuth App:
   - Go to [GitHub Developer Settings](https://github.com/settings/developers)
   - Click "New OAuth App"
   - Fill in:
     - Application name: BLSC
     - Homepage URL: Your website URL
     - Authorization callback URL: Copy from Firebase (looks like `https://your-project.firebaseapp.com/__/auth/handler`)
   - Click "Register application"
   - Copy Client ID and Client Secret to Firebase
4. Click "Save"

## Step 3: Add Your Domain

1. In Firebase Console, go to **Authentication > Settings**
2. Click **Authorized domains**
3. Add your website domain (e.g., `blsc.com`, `localhost`)

## Step 4: Get Firebase Config

1. Go to **Project Settings** (gear icon)
2. Scroll down to "Your apps"
3. Click the web icon `</>`
4. Register your app with a nickname
5. Copy the `firebaseConfig` object

## Step 5: Update auth.html

Replace the config in `auth.html`:

```javascript
const firebaseConfig = {
    apiKey: "YOUR_ACTUAL_API_KEY",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abcdef"
};
```

## That's it!

Now Google and GitHub login will work with real OAuth authentication.

---

## Troubleshooting

### "This domain is not authorized"
- Add your domain in Firebase Console > Authentication > Settings > Authorized domains

### "Google/GitHub login not enabled"
- Enable the provider in Firebase Console > Authentication > Sign-in method

### "Popup closed by user"
- User cancelled the login - this is normal

### "Operation not allowed"
- The sign-in provider is not enabled in Firebase Console
