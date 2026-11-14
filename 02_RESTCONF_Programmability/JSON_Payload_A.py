"""
IETF YANG Interface Payload Blueprint (RFC 8343)
Sanitized RESTCONF JSON-to-Python dictionary template.
"""

IETF_INTERFACE_PAYLOAD = {
    "ietf-interfaces:interfaces": {
        "interface": [
            {
                "name": "GigabitEthernet1",
                "description": "MANAGEMENT INTERFACE",
                "enabled": True,
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": "198.51.100.40",
                            "netmask": "255.255.255.0",
                        }
                    ]
                },
            }
        ]
    }
}

if __name__ == "__main__":
    import json

    print(json.dumps(IETF_INTERFACE_PAYLOAD, indent=2))
