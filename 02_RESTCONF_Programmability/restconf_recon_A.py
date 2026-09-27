
# FILE: restconf_recon_A.py
mock_restconf_payload = {
    "ietf-interfaces:interfaces": {
        "interface": [
            {
                "name": "GigabitEthernet0/0",
                "description": "",
                "type": "iana-if-type:ethernetCsmacd",
                "enabled": True,
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": "192.168.91.130",
                            "netmask": "255.255.255.0"
                        }
                    ]
                }
            },  # <-- Comma keeps the list open for the next item
            {
                "name": "GigabitEthernet0/1",
                "description": "",
                "type": "iana-if-type:",
                "enabled": False,
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": "",
                            "netmask": ""
                        }
                    ]
                }
            },  # <-- Comma keeps the list open for the next item
            {
                "name": "GigabitEthernet0/2",
                "description": "Backup Uplink",
                "type": "iana-if-type:ethernetCsmacd",
                "enabled": True,
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": "10.0.0.2",
                            "netmask": "255.255.255.252"
                        }
                    ]
                }
            },  # <-- Comma keeps the list open for the final item
            {
                "name": "GigabitEthernet0/3",
                "description": "Unconfigured Port",
                "type": "iana-if-type:ethernetCsmacd",
                "enabled": False
            }  # <-- End of fourth interface profile card
        ]  # <-- THIS SQUARE BRACKET MUST SIT HERE TO ENCLOSE ALL 4 PORT PROFILE CARDS!
    }
}





# ======================================================================================
# FILE: restconf_recon_A.py
# CODE EXTRACTION SCRIPT WITH NATIVE DEFENSIVE FILTERS
# ======================================================================================

# ======================================================================================
# STEP 6: ADVANCED EXCEPTION HANDLING (TRY / EXCEPT / RAISE VALUEERROR)
# ======================================================================================
interface_list = mock_restconf_payload["ietf-interfaces:interfaces"]["interface"]

print("\n" + "=" * 50)
print("     OFFICIAL DEVICE INTERFACE AUDIT REPORT     ")
print("=" * 50)

for interface in interface_list:
    # A structural try block tells the interpreter: "Attempt to execute this data parse sweep"
    try:
        interface_name = interface["name"]
        is_enabled = interface["enabled"]

        # Using our safe .get() method to locate the ipv4 nest
        ipv4_container = interface.get("ietf-ip:ipv4")

        if ipv4_container and "address" in ipv4_container:
            # Crucial Trap Check: We access slot 0 of the address list container
            address_block = ipv4_container["address"][0]
            ip_address = address_block["ip"]
            netmask = address_block["netmask"]
        else:
            ip_address = "UNCONFIGURED (L2 or Disabled)"
            netmask = "UNCONFIGURED"

        # Print out the verified operational data profile card
        print(f"Interface Name : {interface_name}")
        print(f"Admin Status   : {'UP' if is_enabled else 'DOWN'}")
        print(f"IPv4 Address   : {ip_address}")
        print(f"Subnet Mask    : {netmask}")
        print("-" * 50)

    except (KeyError, IndexError) as error_token:
        # If the incoming payload format is completely broken, intercept the crash here!
        print(f"CRITICAL MALFORMED PAYLOAD ERROR DETECTED ON PORT: {interface.get('name', 'UNKNOWN')}")
        print("=" * 50)
        # Raise a clean custom error up to the corporate management system
        raise ValueError(f"Automation execution halted. Router data structure is corrupt. Root cause: {error_token}")

print("============ END OF PRODUCTION DEVICE AUDIT ============\n")

