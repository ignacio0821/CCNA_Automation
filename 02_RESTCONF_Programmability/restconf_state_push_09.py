import json
import os
import requests
import urllib3
from yaml_to_restconf_serializer import serialize_yaml_to_json

# Suppress self-signed certificate warnings for local CML testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def save_running_config(host: str, username: str, password: str, headers: dict) -> None:
    """Executes Cisco IOS-XE RESTCONF RPC to save running-config to NVRAM (write memory)."""
    rpc_url = f"https://{host}/restconf/operations/cisco-ia:save-config"
    print(f"[INIT] Executing save-config RPC (write memory) on {host}...")

    try:
        rpc_response = requests.post(
            rpc_url,
            auth=(username, password),
            headers=headers,
            json={},
            verify=False,
            timeout=15,
        )

        if rpc_response.status_code in (200, 204):
            print(
                f"[SUCCESS] HTTP {rpc_response.status_code}: Configuration saved to NVRAM (write memory complete)."
            )
        else:
            print(
                f"[WARNING] Failed to save config via RPC (HTTP {rpc_response.status_code}): {rpc_response.text}"
            )

    except requests.exceptions.RequestException as err:
        print(f"[CONNECTION ERROR] Save-config RPC failed: {err}")


def push_interface_state(yaml_filepath: str) -> None:
    """Ingests YAML intent, forces administrative state, executes HTTP PUT, and saves config."""
    # 1. Target Core-02's live OOB management IP on Gi1
    host = os.getenv("ROUTER_HOST", "192.168.91.135")
    username = os.getenv("ROUTER_USER", "admin")
    password = os.getenv("ROUTER_PASS")

    if not password:
        print("[ABORT] ROUTER_PASS environment variable is not set.")
        return

    # 2. Reuse Step 8 serializer to generate base YANG JSON string
    raw_json_str = serialize_yaml_to_json(yaml_filepath)
    if raw_json_str.startswith("["):
        print(f"[ABORT] Serialization failed:\n{raw_json_str}")
        return

    parsed_dict = json.loads(raw_json_str)

    # 3. Extract the GigabitEthernet dictionary at index
    interface_entry = parsed_dict["Cisco-IOS-XE-native:interface"]["GigabitEthernet"][0]
    interface_id = interface_entry["name"]

    put_payload = {"Cisco-IOS-XE-native:GigabitEthernet": interface_entry}

    # 4. Construct exact RESTCONF resource URI and headers
    url = f"https://{host}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={interface_id}"
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json",
    }

    print(f"[INIT] Pushing state change to {url}...")
    try:
        # 5. Execute HTTP PUT request
        response = requests.put(
            url,
            auth=(username, password),
            headers=headers,
            json=put_payload,
            verify=False,
            timeout=10,
        )

        # 6. Verify immediate sandbox response and persist configuration to NVRAM
        if response.status_code in (200, 201, 204):
            print(
                f"[SUCCESS] HTTP {response.status_code}: Administrative state updated cleanly."
            )
            save_running_config(host, username, password, headers)
        else:
            print(f"[FAILED] HTTP {response.status_code}: {response.text}")

    except requests.exceptions.RequestException as err:
        print(f"[CONNECTION ERROR] Failed to reach sandbox: {err}")


if __name__ == "__main__":
    push_interface_state("interface_provision_2.yaml")
