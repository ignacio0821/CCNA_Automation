import requests
import urllib3
import json

# Disable self-signed SSL certificate alerts
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CLUSTER_INVENTORY = [
    {"hostname": "Core-01", "ip": "192.168.91.132"},
    {"hostname": "Core-02", "ip": "192.168.91.135"},
    {"hostname": "Edge-01", "ip": "192.168.91.134"},
    {"hostname": "Edge-02", "ip": "192.168.91.136"}
]

AUTH = ("admin", "Cisco123")
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

# Explicit Target State Constraint
DESIRED_DOMAIN = "ccna.automation.local"


def enforce_idempotent_domain():
    # Target path pointing straight to the system IP domain name container container
    domain_path = "/restconf/data/Cisco-IOS-XE-native:native/ip/domain"

    print(f"[*] Initializing Cluster State Enforcement Matrix...")
    print(f"[*] Target State Constraint: ip domain name -> '{DESIRED_DOMAIN}'")
    print("=" * 80)

    for device in CLUSTER_INVENTORY:
        url = f"https://{device['ip']}:443{domain_path}"
        print(f"[>] Interrogating {device['hostname']} ({device['ip']})...")

        try:
            # PHASE 1: READ & EVALUATE STATE (The Logic Gate)
            get_res = requests.get(url, headers=HEADERS, auth=AUTH, verify=False, timeout=3)

            current_domain = None
            if get_res.status_code == 200:
                data = get_res.json()
                current_domain = data.get("Cisco-IOS-XE-native:domain", {}).get("name")

            print(f"    - Current State: '{current_domain}'")

            # PHASE 2: MUTATE ONLY IF DRIFT DETECTED (Idempotent Constraint)
            if current_domain == DESIRED_DOMAIN:
                print(f"    [+ STATE VERIFIED ]: Node matches desired state. No mutation required.")
            else:
                print(f"    [! DRIFT DETECTED ]: State mismatch. Deploying RESTCONF payload adjustment...")

                # Payload construction explicitly matching the YANG model schema
                payload = {
                    "Cisco-IOS-XE-native:domain": {
                        "name": DESIRED_DOMAIN
                    }
                }

                # Using PUT to completely overwrite the resource target with our defined state
                put_res = requests.put(
                    url=url,
                    headers=HEADERS,
                    auth=AUTH,
                    data=json.dumps(payload),
                    verify=False,
                    timeout=4
                )

                if put_res.status_code in:
                    print(
                        f"    [+ REPAIR SUCCESS ]: Configuration synchronized successfully (HTTP {put_res.status_code}).")
                else:
                    print(f"    [-] REPAIR FAILED  : Device rejected state update. HTTP Code: {put_res.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"    [-] CRITICAL ERROR : Network socket execution failure: {e}")

        print("-" * 80)


if __name__ == "__main__":
    enforce_idempotent_domain()
