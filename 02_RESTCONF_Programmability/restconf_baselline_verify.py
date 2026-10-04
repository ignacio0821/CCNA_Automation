import requests
import urllib3

# Suppress insecure HTTPS warning outputs inside local/sandbox execution silos
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# STEP 4: CLEAN INVENTORY DICTIONARY BLOCK
TARGET_NODE = {
    "host": "192.168.91.132",
    "port": 443,
    "username": "admin",
    "password": "Cisco123"
}


def verify_data_plane_reachability():
    # Build complete destination URI explicitly
    base_uri = f"https://{TARGET_NODE['host']}:{TARGET_NODE['port']}"
    target_path = "/restconf/data/Cisco-IOS-XE-native:native"
    full_url = f"{base_uri}{target_path}"

    # Fully qualified media types
    strict_headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json"
    }

    explicit_auth = (TARGET_NODE["username"], TARGET_NODE["password"])

    print(f"[*] Initializing outbound baseline GET to: {TARGET_NODE['host']}")

    try:
        response = requests.get(
            url=full_url,
            headers=strict_headers,
            auth=explicit_auth,
            timeout=5,
            verify=False  # Required bypass for self-signed certificates
        )

        # Interrogate return codes cleanly
        if response.status_code == 200:
            print("[+] SYSTEM CAPTURE SUCCESSFUL (200 OK)")
            print(f"[+] Native configuration payload character length: {len(response.text)}")
            return True
        else:
            print(f"[-] Target rejected connection. HTTP Status Code: {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print("[-] Failure Error: Connection timed out. Check routing configuration or firewalls.")
        return False
    except requests.exceptions.RequestException as error_msg:
        print(f"[-] Structural Connection Failure: {error_msg}")
        return False


if __name__ == "__main__":
    verify_data_plane_reachability()
