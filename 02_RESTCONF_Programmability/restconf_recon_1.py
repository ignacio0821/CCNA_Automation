# =========================================================================
# FILE: restconf_recon.py
# DIRECTORY: 6_restconf_data_model_recon
# DESCRIPTION: Production-Grade RESTCONF Live Network Telemetry Auditor
# =========================================================================

import urllib3
import requests
from requests.auth import HTTPBasicAuth

# Suppress local self-signed SSL certificate tracking warnings in our lab
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    # 1. Transport Layer Setup Configuration
    ROUTER_IP = "192.168.91.132"
    URL = f"https://{ROUTER_IP}/restconf/data/Cisco-IOS-XE-native:native/interface"

    # Production RFC 8040 Header Matrix targeting YANG-modeled JSON
    HEADERS = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json"
    }

    # Live credentials for the virtualized laboratory node
    AUTH = HTTPBasicAuth("admin", "Cisco123")

    print("\n" + "=" * 55)
    print("INITIALIZING WIRE TELEMETRY PULL FROM GATEWAY ROUTER...")
    print("=" * 55)

    try:
        # 2. Secure Transport Execution over Port 443 TLS
        response = requests.get(
            url=URL,
            headers=HEADERS,
            auth=AUTH,
            verify=False  # Bypass SSL check for sandbox isolation safety
        )

        # Intercept HTTP errors (e.g., 401 Unauthorized, 404 Not Found) before parsing
        response.raise_for_status()

        # Ingest raw network JSON text data into a Python dictionary object
        network_data = response.json()

        # 3. Navigate Document Structural Tree Boundary cleanly
        interface_list = network_data["Cisco-IOS-XE-native:interface"]["GigabitEthernet"]

        print("\n" + "=" * 55)
        print("         OFFICIAL LIVE CORE DEVICE AUDIT REPORT         ")
        print("=" * 55)

        # 4. Step 6 Abstract Logic Gate Iteration Loop Transformation
        for GigabitEthernet in interface_list:
            # Extract mandatory naming identifier identifier
            interface_name = GigabitEthernet["name"]

            # Key Membership Detection: True if port is disabled, False if active
            is_disabled = "shutdown" in GigabitEthernet
            admin_status = "DOWN" if is_disabled else "UP"

            # Defensively drill into nested IP schemas to prevent KeyErrors
            ip_container = GigabitEthernet.get("ip", {})
            address_container = ip_container.get("address", {})

            # Conditional Validation Matrix for IP Assignment Type Architecture
            if "dhcp" in address_container:
                ip_address = "DYNAMIC (DHCP Assigned)"
                netmask = "DYNAMIC (DHCP Assigned)"
            elif "primary" in address_container:
                primary_block = address_container.get("primary", {})
                ip_address = primary_block.get("address", "UNCONFIGURED")
                netmask = primary_block.get("netmask", "UNCONFIGURED")
            else:
                ip_address = "UNCONFIGURED (Layer-2 / Switchport)"
                netmask = "UNCONFIGURED"

            # Emit clean output card records
            print(f"Interface Name  : GigabitEthernet{interface_name}")
            print(f"Admin Status    : {admin_status}")
            print(f"IPv4 Address    : {ip_address}")
            print(f"Subnet Mask     : {netmask}")
            print("-" * 55)

        print("============= END OF PRODUCTION DEVICE AUDIT =============\n")

    except requests.exceptions.HTTPError as http_error:
        print(f"\n[!] TRANSPORT FAILURE: HTTP protocol failure. Code: {response.status_code}")
        print(f"Details: {http_error}")
    except requests.exceptions.ConnectionError:
        print(f"\n[!] LINK FAILURE: Cannot establish socket with router at {ROUTER_IP}.")
        print("Verify CML node state, routing paths, and that RESTCONF is enabled via 'restconf'.")
    except (KeyError, TypeError) as schema_error:
        print(f"\n[!] SCHEMA MISMATCH: The incoming YANG data structure layout has drifted.")
        print(f"Root parsing error: {schema_error}")


if __name__ == "__main__":
    main()
