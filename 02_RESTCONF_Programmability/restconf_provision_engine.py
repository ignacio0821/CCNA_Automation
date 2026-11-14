import os
import yaml
import urllib3
import requests
from dotenv import load_dotenv

# Suppress SSL validation banners from local CML environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load decoupled system credentials out of your Local .env Layer
load_dotenv()
username = os.getenv("RESTCONF_USER")
password = os.getenv("RESTCONF_PASS")
auth_credentials = (username, password)

# Define standard headers using canonical YANG data-model media types
restconf_headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}

# Define the relative path to our target configuration file
yaml_file_path = "interface_provision_1.yaml"

print(f"[+] Ingesting structured configuration template: {yaml_file_path}")

# Open and safely deserialize the YAML file into a native Python dictionary
with open(yaml_file_path, "r") as file:
    config_data = yaml.safe_load(file)

print("[*] Configuration template successfully parsed into memory.")

# Unpack the deserialized YAML dictionary layers safely into intermediate variables
target_block = config_data.get("target_interface", {})
intf_type = target_block.get("type")
intf_name = str(target_block.get("slot_id"))

state_block = target_block.get("configuration_state", {})
description_str = state_block.get("description")
enabled_bool = state_block.get("enabled")

ip_block = state_block.get("ip_assignment", {})
ipv4_addr = ip_block.get("ipv4_address")
subnet_mask = ip_block.get("subnet_mask")

# Reconstruct variables into a canonical Cisco Native JSON PATCH Layout
mutated_payload = {
    f"Cisco-IOS-XE-native:{intf_type}": [
        {
            "name": intf_name,
            "description": description_str,
            "ip": {
                "address": {
                    "primary": {
                        "address": ipv4_addr,
                        "mask": subnet_mask,
                    }
                }
            },
        }
    ]
}

# Define our multi-node targeting Loop (testing on your Edge-01 node first)
TARGET_NODE = "192.168.91.132"
print(f"\n[>] Executing Programmatic State Push to Endpoint: {TARGET_NODE}")

# Construct the targeted URI string pointing directly to GigabitEthernet=2
push_url = f"https://{TARGET_NODE}/restconf/data/Cisco-IOS-XE-native:native/interface/{intf_type}={intf_name}"

try:
    # Issue a state-changing HTTP PATCH request to update the target attributes
    mutation_response = requests.patch(
        url=push_url,
        headers=restconf_headers,
        json=mutated_payload,
        auth=auth_credentials,
        verify=False,
        timeout=5.0,
    )

    # An HTTP 24 No Content status code is standard for a successful RESTCONF PATCH
    if mutation_response.status_code in [200, 201, 204]:
        print(
            f"[+] SUCCESS: State mutation successfully committed to Node {TARGET_NODE}!"
        )
    else:
        print(
            f"[-] WARNING: Unexpected server status returned: {mutation_response.status_code}"
        )

except requests.exceptions.RequestException as err:
    print(f"[-] CRITICAL ENGINE BLOCKED: State push filed over network wire: {err}")
