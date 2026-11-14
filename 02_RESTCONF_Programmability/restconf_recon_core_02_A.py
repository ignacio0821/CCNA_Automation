# =========================================================================
# FILE: restconf_recon_core-02_A.py
# DESCRIPTION: Production-grade Cisco IOS-XE YANG Payload Parsing Script
# =========================================================================

# Simulated production router payload captured directly from CML/Postman
restconf_core_02_A_payload = {
    "Cisco-IOS-XE-native:interface": {
        "GigabitEthernet": [
            {
                "name": "1",
                "description": "HOST_BRIDGE_TRANSIT",
                "ip": {
                    "address": {
                        "dhcp": {}
                    }
                },
                "Cisco-IOS-XE-ethernet:negotiation": {
                    "auto": True
                }
            },
            {
                "name": "2",
                "description": "OOB_PRODUCTION_BACKBONE",
                "ip": {
                    "address": {
                        "primary": {
                            "address": "10.255.0.12",
                            "mask": "255.255.255.0"
                        }
                    }
                },
                "ipv6": {
                    "address": {
                        "prefix-list": [
                            {
                                "prefix": "2001:DB8:CCAA::12/64"
                            }
                        ]
                    }
                },
                "Cisco-IOS-XE-ethernet:negotiation": {
                    "auto": True
                }
            },
            {
                "name": "3",
                "shutdown": [
                    None
                ],
                "Cisco-IOS-XE-ethernet:negotiation": {
                    "auto": True
                }
            },
            {
                "name": "4",
                "shutdown": [
                    None
                ],
                "Cisco-IOS-XE-ethernet:negotiation": {
                    "auto": True
                }
            }
        ]
    }
}

# STEP 1: Safely isolate the core list array from the dictionary structure
interface_list = restconf_core_02_A_payload["Cisco-IOS-XE-native:interface"]["GigabitEthernet"]

# Print header metadata
print("\n" + "=" * 50)
print("     OFFICIAL DEVICE INTERFACE AUDIT REPORT     ")
print("=" * 50)

# STEP 2: Execute iteration loop using unified block tokens
for GigabitEthernet in interface_list:
    try:
        # Extract mandatory naming identifier
        interface_name = GigabitEthernet["name"]

        ipv6_addresses = []

        # Membership check: True if 'shutdown' key exists (port is down), False if active (port is up)
        is_disabled = "shutdown" in GigabitEthernet
        admin_status = "DOWN" if is_disabled else "UP"

        # Safely navigate nested layers using chained .get() lookups to avoid KeyErrors
        address_container = GigabitEthernet.get("ip", {}).get("address", {})

        # Determine IP Assignment Mechanism (DHCP vs. Static vs. Unconfigured)
        if "dhcp" in address_container:
            ip_address = "DYNAMIC (DHCP Assigned)"
            netmask = "DYNAMIC (DHCP Assigned)"
        elif "primary" in address_container:
            primary_block = address_container.get("primary", {})
            ip_address = primary_block.get("address", "UNCONFIGURED")
            netmask = primary_block.get("netmask", "UNCONFIGURED")
        else:
            ip_address = "UNCONFIGURED (L2 or Disabled)"
            netmask = "UNCONFIGURED"

            # Determine IPv6 Assignment Mechanism (Defensive Array Sub-Loop)
            ipv6_container = GigabitEthernet.get("ipv6", {}).get("address", {})

            if "prefix-list" in ipv6_container:
                prefix_list = ipv6_container.get("prefix-list", [])
                for prefix_entry in prefix_list:
                    if isinstance(prefix_entry, dict) and "prefix" in prefix_entry:
                        ipv6_addresses.append(prefix_entry.get("prefix"))

            if not ipv6_addresses:
                ipv6_addresses.append("UNCONFIGURED (L2 or Disabled)")

        # Output the parsed telemetry record profile card
        print(f"Interface Name  : GigabitEthernet{interface_name}")
        print(f"Admin Status    : {admin_status}")
        print(f"IPv4 Address    : {ip_address}")
        print(f"Subnet Mask     : {netmask}")
        print("-" * 50)

        print(f"IPv6 Prefix     : {', '.join(ipv6_addresses)}")


    except (KeyError, IndexError) as error_token:
        # Fallback tracking if a specific entry block structure breaks
        broken_port = GigabitEthernet.get('name', 'UNKNOWN')
        print(f"CRITICAL MALFORMED PAYLOAD ERROR DETECTED ON PORT: {broken_port}")
        print("=" * 50)
        raise ValueError(
            f"Automation execution halted. Router data structure is corrupt. "
            f"Target Port: {broken_port}. Root cause: {error_token}"
        )

# Global footer snapped directly to the left margin out of loop scope
print("============= END OF PRODUCTION DEVICE AUDIT =============\n")