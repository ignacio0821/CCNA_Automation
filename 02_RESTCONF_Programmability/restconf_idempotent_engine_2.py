# ==============================================================================
# SCRIPT: restconf_idempotent_engine_1.py
# TRACK:  02_RESTCONF_Programmability
# TARGET: CCNAAUTO Multi-Node Cluster State Verification & Idempotency Loop
# ==============================================================================

import os
import urllib3
import requests
from dotenv import load_dotenv

# Suppress SSL certificate validation warnings in local CML sandboxes
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ingest environmental key-value pairs from your local active .env file
load_dotenv()

# Multi-Node Target Inventory Core Matrix
CLUSTER_NODES = ["192.168.91.132", "192.168.91.135", "192.168.91.134", "192.168.91.136"]

# Safely extract credentials from decoupled environment layer
username = os.getenv("RESTCONF_USER")
password = os.getenv("RESTCONF_PASS")
auth_credentials = (username, password)

# RFC 8040 Canonical YANG Data-Model Header Media Types
restconf_headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

# Iterate through each physical node in our isolated CML environment
for node in CLUSTER_NODES:
    print(f"\n[+] Initializing Baseline Scan for Edge Node: {node}")

    # Target URL pointing to the Cisco IOS-XE Native Interface container root
    target_url = f"https://{node}/restconf/data/Cisco-IOS-XE-native:native/interface"

    try:
        # Execute the synchronous network GET request with strict timeouts
        response = requests.get(
            url=target_url,
            headers=restconf_headers,
            auth=auth_credentials,
            verify=False,
            timeout=5.0  # Guard window to prevent infinite script hanging
        )

        # Catch unexpected HTTP server errors (4xx / 5xx) before parsing keys
        response.raise_for_status()

        # Unpack the raw text string into a native Python dictionary
        response_data = response.json()

        # Traverse safely down to the media type array list layer
        interfaces_list = response_data.get("Cisco-IOS-XE-native:interface", {}).get("GigabitEthernet", [])

        # GATE 1: Iterate through each physical slot block returned by the router
        for intf in interfaces_list:

            # GATE 2: Filter and isolate our target physical edge port
            if str(intf.get("name")) == "2":

                # GATE 3: Safely evaluate configuration alignment to protect the loop
                current_description = intf.get("description")
                target_template = "DOM_PRODUCTION_BACKBONE"

                if current_description == target_template:
                    print(
                        f"[*] IDEMPOTENT BYPASS: Node {node} GigabitEthernet2 description is already aligned. Skipping mutation.")
                else:
                    print(f"[!] STATE MISMATCH IDENTIFIED: Node {node} description is: '{current_description}'")
                    print(f"[>] Action: Initializing configuration state modification sequence...")

    except requests.exceptions.Timeout:
        print(f"[-] CRITICAL ERROR: Connection timed out on target node {node}. Bypassing...")
        continue

    except requests.exceptions.HTTPError as http_err:
        status_code = response.status_code
        print(f"[-] API ERROR: Node {node} returned HTTP Status Code: {status_code}. Bypassing...")
        continue

    except requests.exceptions.RequestException as general_err:
        print(f"[-] SYSTEM FAULT: Unhandled connection anomaly on node {node}: {general_err}")
        continue
