# 🔥 Firebase ማዋቀር - በአማርኛ

## Firebase ምንድን ነው?
Firebase የGoogle ነፃ የደመና አገልግሎት ነው። ተጠቃሚዎችዎ ከየትኛውም ቦታ መመዝገብ እና መግባት ይችላሉ - ልክ እንደ Google መለያ!

---

## 📋 ደረጃ በደረጃ መመሪያ

### ደረጃ 1: Firebase Console ይክፈቱ
1. ወደ https://console.firebase.google.com/ ይሂዱ
2. በGoogle መለያዎ ይግቡ (Gmail)
3. "Create a project" ወይም "ፕሮጀክት ፍጠር" ይጫኑ

### ደረጃ 2: አዲስ ፕሮጀክት ይፍጠሩ
1. የፕሮጀክት ስም ያስገቡ: `blsc-accounts` (ወይም የፈለጉትን)
2. "Continue" ይጫኑ
3. Google Analytics ያስፈልግዎታል? "No" ይምረጡ (ለቀላልነት)
4. "Create project" ይጫኑ
5. ጥቂት ሰከንዶች ይጠብቁ...
6. "Continue" ይጫኑ

### ደረጃ 3: Firestore Database ይፍጠሩ
1. በግራ በኩል "Build" ይጫኑ
2. "Firestore Database" ይምረጡ
3. "Create database" ይጫኑ
4. **"Start in test mode"** ይምረጡ (ለጊዜው ለሙከራ)
5. Location: `eur3 (europe-west)` ወይም ቅርብዎን ይምረጡ
6. "Enable" ይጫኑ

### ደረጃ 4: Web App ያክሉ
1. በፕሮጀክት ገጽ ላይ ⚙️ (Settings) ይጫኑ
2. "Project settings" ይምረጡ
3. ወደ ታች ይሸብልሉ "Your apps" ክፍል
4. **</>** (Web) አዶውን ይጫኑ
5. App nickname: `BLSC Website` ያስገቡ
6. "Register app" ይጫኑ

### ደረጃ 5: Configuration ይቅዱ
ይህን የሚመስል ኮድ ያያሉ:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyB1234567890abcdefg",
  authDomain: "blsc-accounts.firebaseapp.com",
  projectId: "blsc-accounts",
  storageBucket: "blsc-accounts.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef123456"
};
```

**ይህን ሙሉ በሙሉ ይቅዱ!**

### ደረጃ 6: ኮድዎን ያዘምኑ
1. `blsc-account-firebase.js` ፋይል ይክፈቱ
2. የድሮውን `firebaseConfig` በአዲሱ ይተኩ
3. ፋይሉን ያስቀምጡ

---

## 🔧 ኮድ ለውጦች

### auth.html ውስጥ ይህን ያክሉ (ከ </head> በፊት):

```html
<!-- Firebase Scripts -->
<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore-compat.js"></script>
```

### blsc-account.js ን በ blsc-account-firebase.js ይተኩ:
ሁሉም HTML ፋይሎች ውስጥ:
```html
<!-- ከዚህ -->
<script src="blsc-account.js"></script>

<!-- ወደዚህ ይቀይሩ -->
<script src="blsc-account-firebase.js"></script>
```

---

## ✅ ሙከራ ያድርጉ

1. ድረ-ገጽዎን ይክፈቱ
2. አዲስ መለያ ይፍጠሩ
3. Firebase Console ይመልከቱ → Firestore Database
4. "users" collection ውስጥ አዲሱን ተጠቃሚ ያያሉ!

---

## 🔒 ደህንነት (ለወደፊት)

ከሙከራ በኋላ፣ Firestore Rules ያዘምኑ:

1. Firebase Console → Firestore Database → Rules
2. ይህን ያስገቡ:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if true; // ለጊዜው ሁሉም ይፈቀዳል
    }
  }
}
```

---

## 💰 ዋጋ

Firebase Spark Plan (ነፃ):
- 1GB ማከማቻ
- 50,000 ንባቦች/ቀን
- 20,000 ጽሁፎች/ቀን
- ለአነስተኛ ድረ-ገጽ በቂ ነው!

---

## 🆘 ችግር ካጋጠመዎት

### "Permission denied" ስህተት
→ Firestore Rules "test mode" ላይ መሆኑን ያረጋግጡ

### "Firebase is not defined" ስህተት
→ Firebase scripts በትክክል መጫናቸውን ያረጋግጡ

### ተጠቃሚዎች አይታዩም
→ Browser Console (F12) ውስጥ ስህተቶችን ይመልከቱ

---

## 📞 ተጨማሪ እርዳታ

- Firebase Docs: https://firebase.google.com/docs
- YouTube Tutorials: "Firebase Firestore tutorial" ይፈልጉ

---

**መልካም ስራ! 🎉**
