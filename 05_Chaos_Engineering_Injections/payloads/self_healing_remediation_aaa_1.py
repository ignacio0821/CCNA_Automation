import os
import urllib3
import requests
from netmiko import ConnectHandler
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

TARGET_NODE = "192.168.91.132"
username = os.getenv("RESTCONF_USER")
password = os.getenv("RESTCONF_PASS")

# RECONSTRUCTED PROFILE: Use a direct generic driver terminal mapping
ssh_device_profile = {
    "device_type": "cisco_xe_ssh",  # Standard driver channel
    "host": TARGET_NODE,
    "username": username,
    "password": password,
    "fast_cli": False,  # Slow down pacing to avoid buffer overrun
}

restconf_headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
push_url = f"https://{TARGET_NODE}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=2"
mutated_payload = {"Cisco-IOS-XE-native:GigabitEthernet": [{"name": "2", "description": "DOM_PRODUCTION_BACKBONE"}]}


def execute_state_push():
    print(f"[>] Attempting RESTCONF State Push to Node: {TARGET_NODE}")
    response = requests.patch(url=push_url, headers=restconf_headers, json=mutated_payload, auth=(username, password),
                              verify=False, timeout=3.0)
    response.raise_for_status()


try:
    # Attempt our standard automation API flight
    execute_state_push()
    print(f"[+] SUCCESS: Network state is aligned on Node {TARGET_NODE}.")

except requests.exceptions.HTTPError as http_err:
    if http_err.response.status_code == 401:
        print(f"[!] SELF-HEALING TRIGGERED: Caught AAA authorization lockout (401) on Node {TARGET_NODE}!")
        print("[>] Pushing programmatic configuration restoration via Netmiko stream...")

        # Connect and push the repair commands as a single atomic data block
        connection = ConnectHandler(**ssh_device_profile)

        # Force config configuration bypass commands straight to the terminal background executor
        repair_commands = ["aaa authorization exec default local"]
        connection.send_config_set(repair_commands)
        connection.disconnect()

        print("[+] Programmatic remediation complete. Re-executing RESTCONF validation...")

        # Re-attempt the RESTCONF state push now that the gate is healed
        execute_state_push()
        print("[++ ] CRITICAL SUCCESS: Control plane healed programmatically. State push committed!")
