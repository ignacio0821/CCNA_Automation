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

# Build the alternate transport SSH profile for self-healing injection
ssh_device_profile = {
    "device_type": "cisco_xe",
    "host": TARGET_NODE,
    "username": username,
    "password": password,
}

restconf_headers = {"Accept": "application/yang-data+json", "Content-Type": "application/yang-data+json"}
push_url = f"https://{TARGET_NODE}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=2"
mutated_payload = {"Cisco-IOS-XE-native:GigabitEthernet": [{"name": "2", "description": "DOM_PRODUCTION_BACKBONE"}]}


def execute_state_push():
    print(f"[>] Attempting RESTCONF State Push to Node: {TARGET_NODE}")
    response = requests.patch(url=push_url, headers=restconf_headers, json=mutated_payload, auth=(username, password),
                              verify=False, timeout=3.0)
    response.raise_for_status()


try:
    # Attempt the happy-path configuration change
    execute_state_push()
    print(f"[+] SUCCESS: Network state is aligned on Node {TARGET_NODE}.")

except requests.exceptions.HTTPError as http_err:
    if http_err.response.status_code == 401:
        print(f"[!] SELF-HEALING TRIGGERED: Caught AAA authorization lockout (401) on Node {TARGET_NODE}!")
        print("[>] Deploying Netmiko alternate transport channel to remediate control plane...")

        # Open programmatic SSH channel to dynamically push the recovery command string
        with ConnectHandler(**ssh_device_profile) as ssh_tunnel:
            reremed_commands = ["aaa authorization exec default local"]
            ssh_tunnel.send_config_set(reremed_commands)

        print("[+] Programmatic remediation complete. Re-executing RESTCONF state validation...")

        # Automatically re-verify state over the wire to complete the self-healing cycle
        execute_state_push()
        print(f"[++ ] CRITICAL SUCCESS: Control plane healed programmatically. State push committed!")
