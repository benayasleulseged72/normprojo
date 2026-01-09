"""
BLSC Brute Force Password Guessing Game
Educational simulation tool - Enter a password and watch it get cracked!
© 2026 BENAYAS LEULSEGED Software Company
"""

import time
import string
import os
import sys

# Colors for terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
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
║            Password Guessing Game v1.0                       ║
║            Educational Purpose Only                          ║
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
        print(f"{Colors.RED}[*] {text}{Colors.RESET}")
    else:
        print(f"{Colors.CYAN}[*] {text}{Colors.RESET}")

def get_charset(options):
    charset = ""
    if 'l' in options:
        charset += string.ascii_lowercase
    if 'u' in options:
        charset += string.ascii_uppercase
    if 'n' in options:
        charset += string.digits
    if 's' in options:
        charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return charset if charset else string.ascii_lowercase + string.digits

def display_progress(found_chars, target_length, attempts, elapsed):
    progress = len([c for c in found_chars if c is not None]) / target_length * 100
    bar_length = 40
    filled = int(bar_length * progress / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    password_display = ""
    for i, char in enumerate(found_chars):
        if char is not None:
            password_display += f"{Colors.GREEN}{char}{Colors.RESET}"
        else:
            password_display += f"{Colors.RED}×{Colors.RESET}"
    
    print(f"\r{Colors.CYAN}Password: [{password_display}{Colors.CYAN}] | Progress: [{Colors.GREEN}{bar}{Colors.CYAN}] {progress:.1f}% | Attempts: {attempts:,} | Time: {elapsed:.2f}s{Colors.RESET}", end="", flush=True)

def brute_force_attack(target_password, charset, speed=0.05):
    """
    Simulate brute force attack on the target password
    """
    target_length = len(target_password)
    found_chars = [None] * target_length
    attempts = 0
    start_time = time.time()
    
    print(f"\n{Colors.YELLOW}{'='*60}{Colors.RESET}")
    print_status(f"Target password length: {target_length} characters", "attack")
    print_status(f"Charset size: {len(charset)} characters", "attack")
    print_status("Starting brute force attack...", "attack")
    print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}\n")
    
    for pos in range(target_length):
        target_char = target_password[pos]
        
        # Try each character in charset
        for char in charset:
            attempts += 1
            elapsed = time.time() - start_time
            
            # Update display
            temp_chars = found_chars.copy()
            temp_chars[pos] = char
            display_progress(temp_chars, target_length, attempts, elapsed)
            
            time.sleep(speed)
            
            if char == target_char:
                found_chars[pos] = char
                break
        
        # If character not in charset, still find it
        if found_chars[pos] is None:
            attempts += 1
            found_chars[pos] = target_char
            elapsed = time.time() - start_time
            display_progress(found_chars, target_length, attempts, elapsed)
    
    elapsed = time.time() - start_time
    print("\n")
    
    return "".join(found_chars), attempts, elapsed

def main():
    while True:
        clear_screen()
        print_banner()
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.WHITE}Enter a password and watch the system crack it!{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
        
        # Get target password
        target = input(f"{Colors.GREEN}[>] Enter password to crack: {Colors.WHITE}")
        
        if not target:
            print_status("Please enter a password!", "error")
            time.sleep(1)
            continue
        
        # Get charset options
        print(f"\n{Colors.CYAN}Select character sets to use:{Colors.RESET}")
        print(f"  {Colors.WHITE}[l]{Colors.RESET} Lowercase (a-z)")
        print(f"  {Colors.WHITE}[u]{Colors.RESET} Uppercase (A-Z)")
        print(f"  {Colors.WHITE}[n]{Colors.RESET} Numbers (0-9)")
        print(f"  {Colors.WHITE}[s]{Colors.RESET} Special (!@#$...)")
        print(f"\n{Colors.YELLOW}Example: 'ln' for lowercase + numbers{Colors.RESET}")
        
        options = input(f"{Colors.GREEN}[>] Enter options (default: ln): {Colors.WHITE}").lower()
        if not options:
            options = "ln"
        
        charset = get_charset(options)
        
        # Get speed
        print(f"\n{Colors.CYAN}Select attack speed:{Colors.RESET}")
        print(f"  {Colors.WHITE}[1]{Colors.RESET} Slow (visual)")
        print(f"  {Colors.WHITE}[2]{Colors.RESET} Medium")
        print(f"  {Colors.WHITE}[3]{Colors.RESET} Fast")
        
        speed_choice = input(f"{Colors.GREEN}[>] Enter speed (default: 2): {Colors.WHITE}")
        speeds = {'1': 0.1, '2': 0.05, '3': 0.01}
        speed = speeds.get(speed_choice, 0.05)
        
        # Start attack
        print(f"\n{Colors.RED}{Colors.BOLD}")
        print("  ╔═══════════════════════════════════════╗")
        print("  ║     INITIATING BRUTE FORCE ATTACK     ║")
        print("  ╚═══════════════════════════════════════╝")
        print(f"{Colors.RESET}")
        
        time.sleep(1)
        
        cracked, attempts, elapsed = brute_force_attack(target, charset, speed)
        
        # Results
        print(f"{Colors.GREEN}{'='*60}{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}")
        print("  ╔═══════════════════════════════════════╗")
        print("  ║         PASSWORD CRACKED!             ║")
        print("  ╚═══════════════════════════════════════╝")
        print(f"{Colors.RESET}")
        
        print(f"\n{Colors.WHITE}  Password: {Colors.GREEN}{Colors.BOLD}{cracked}{Colors.RESET}")
        print(f"{Colors.WHITE}  Attempts: {Colors.CYAN}{attempts:,}{Colors.RESET}")
        print(f"{Colors.WHITE}  Time:     {Colors.CYAN}{elapsed:.2f} seconds{Colors.RESET}")
        print(f"{Colors.WHITE}  Speed:    {Colors.CYAN}{int(attempts/elapsed):,} attempts/sec{Colors.RESET}")
        print(f"\n{Colors.GREEN}{'='*60}{Colors.RESET}")
        
        # Continue?
        again = input(f"\n{Colors.YELLOW}[?] Try another password? (y/n): {Colors.WHITE}").lower()
        if again != 'y':
            print(f"\n{Colors.GREEN}Thanks for using BLSC Brute Force!{Colors.RESET}")
            print(f"{Colors.CYAN}© 2026 BENAYAS LEULSEGED Software Company{Colors.RESET}\n")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!] Attack cancelled by user.{Colors.RESET}")
        print(f"{Colors.GREEN}Thanks for using BLSC Brute Force!{Colors.RESET}\n")
        sys.exit(0)
