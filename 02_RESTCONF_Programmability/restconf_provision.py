# =========================================================================
# FILE: restconf_provision.py
# DIRECTORY: 6_restconf_data_model_recon
# DESCRIPTION: Production-Grade RESTCONF YAML Provisioning Engine (Step 9)
# =========================================================================

import os
import yaml
import urllib3
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Automatically scan for and ingest variables from your hidden local .env sheet
load_dotenv()

# Suppress local self-signed SSL tracking warnings in our sandbox lab
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_yaml_template(file_path):
    """Ingests local YAML configuration file and returns a structured dictionary."""
    with open(file_path, "r") as file_stream:
        return yaml.safe_load(file_stream)


def main():
    # 1. Ingest YAML configuration file template (Step 9 Data Ingestion)
    yaml_data = load_yaml_template("interface_provision.yaml")
    config_block = yaml_data["cisco_ios_xe_interface_update"]

    # ABSTRACTED VARIABLES: Pull targets cleanly from local environment memory
    router_ip = os.getenv("CML_ROUTER_IP")
    username = os.getenv("CML_USERNAME")
    password = os.getenv("CML_PASSWORD")

    # Establish unified authentication scope
    auth = HTTPBasicAuth(username, password)

    print("\n" + "=" * 60)
    print(f"INGESTED YAML TEMPLATE FOR TARGET ROUTER: {router_ip}")
    print("=" * 60)

    # 2. Iterate through your defined interface data list objects
    # 2. Iterate through your defined interface data list objects
    # 2. Iterate through your defined interface data list objects
    for interface in config_block["interfaces"]:
        port_id = interface["name"]
        description = interface["description"]
        ip_addr = interface["ip_address"]
        subnet_mask = interface["netmask"]

        # Target the individual interface leaf key path directly in the URL
        url = f"https://{router_ip}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={port_id}"

        headers = {
            "Accept": "application/yang-data+json",
            "Content-Type": "application/yang-data+json"
        }

        auth = HTTPBasicAuth("admin", "Cisco123")

        # 3. Translate flat YAML into strict targeted individual leaf attributes
        # Changed the inner key token from "netmask" to the native Cisco "mask" parameter
        yang_payload = {
            "Cisco-IOS-XE-native:GigabitEthernet": {
                "name": port_id,
                "description": description,
                "ip": {
                    "address": {
                        "primary": {
                            "address": ip_addr,
                            "mask": subnet_mask  # <-- Core Cisco YANG model fix
                        }
                    }
                }
            }
        }

        # Handle the administrative status toggle configuration block
        if interface["status"].upper() != "UP":
            yang_payload["Cisco-IOS-XE-native:GigabitEthernet"]["shutdown"] = [None]

        print(f"\n[+] Provisioning GigabitEthernet{port_id} via individual leaf endpoint...")
        print(f"    IP Target   : {ip_addr} / {subnet_mask}")
        print(f"    Description : {description}")

        try:
            # 4. Execute the Programmatic State Push using HTTP PATCH
            response = requests.patch(
                url=url,
                headers=headers,
                auth=auth,
                json=yang_payload,
                verify=False
            )

            response.raise_for_status()

            # A successful RESTCONF PATCH configuration merge returns an explicit 204 No Content code
            if response.status_code in [200, 204]:
                print(f"----> SUCCESS: GigabitEthernet{port_id} merged cleanly. Status: {response.status_code}")

        except requests.exceptions.HTTPError as http_err:
            print(f"----> [!] PROVISIONING FAILED ON PORT {port_id}. Code: {response.status_code}")
            print(f"      Payload Sent: {yang_payload}")
            print(f"      Root Cause  : {http_err}")

            # =================================================================
            # STEP 11: AUTOMATED SELF-HEALING REMEDIATION ACTIVE TRIGGER
            # =================================================================
            print(f"\n[!] TRIGGERING STEP 11: SELF-HEALING REMEDIATION ON PORT {port_id}...")

            # Define a secure, unconfigured fallback state payload with the correct native 'mask' key
            self_healing_payload = {
                "Cisco-IOS-XE-native:GigabitEthernet": {
                    "name": port_id,
                    "description": "REMEDIATED_BY_AUTOMATION_BASLINE_FALLBACK",
                    "ip": {
                        "address": {
                            "primary": {
                                "address": "10.254.254.254",  # Safe quarantine sandbox IP
                                "mask": "255.255.255.252"
                            }
                        }
                    }
                }
            }

            try:
                # Force an immediate corrective PATCH to overwrite the corrupted state configuration
                remediation_response = requests.patch(
                    url=url,
                    headers=headers,
                    auth=auth,
                    json=self_healing_payload,
                    verify=False
                )
                remediation_response.raise_for_status()
                print(
                    f"----> SELF-HEAL SUCCESS: Port {port_id} safely quarantined to baseline. Code: {remediation_response.status_code}")
                print("-" * 55)
            except requests.exceptions.RequestException as fatal_heal_error:
                print(
                    f"----> [CRITICAL] SELF-HEALING FAILURE: Unable to remediate device layer. Details: {fatal_heal_error}")
                print("-" * 55)


if __name__ == "__main__":
    main()
