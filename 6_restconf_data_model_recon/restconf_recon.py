# ======================================================================================
# FILE: restconf_recon.py
# STEP 4: DATA MODEL RECON (STRUCTURED BLUEPRINT)
# ======================================================================================

# 1. THE DATA ENVIRONMENT MOCK
# This dictionary mimics the exact JSON payload structured response from a Cisco device.
mock_restconf_payload = {
    "ietf-interfaces:interfaces": {
        "interface": [
            {
                "name": "GigabitEthernet0/0",
                "description": "Primary Management Uplink",
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
            }
        ]
    }
}

# 2. THE ABSTRACT LOGIC ENTRY GATE
# Write out your structured pseudocode below this line to plan how you will target
# and extract the specific "name" and "ip" values from the nested data dictionary.
# ======================================================================================
# STEP 5 NESTED LOGIC MAP: TARGETING THE DATA CODES
# ======================================================================================
#
# GATE 1: THE ROOT CONTAINER DICTIONARY
#         - Your variable 'mock_restconf_payload' is the main warehouse door.
#         - Inside, it contains exactly one primary tag key: "ietf-interfaces:interfaces".
#         - Logic Action: You must step through this key first to see what's inside.
#
# AISLE 2: THE INTERFACE CONTAINER LIST
#         - Inside the root container sits a child key named "interface".
#         - Crucial Trap: Look closely at line 10 in your file. Notice the square bracket '['.
#           This means "interface" holds a LIST of items, not a single dictionary.
#         - Logic Action: You must look inside the very first slot of this list
#           (Index position 0) to grab the interface profile box.
#
# BOX 3: THE SPECIFIC TARGET LABELS
#         - Now that you are inside the first profile box, the data branches:
#
#         * TARGET A: THE INTERFACE NAME
#           - Look directly at the key named "name".
#           - Logic Action: Read its value directly ("GigabitEthernet0/0"). Target A locked.
#
#         * TARGET B: THE IPV4 SUBNET NEST
#           - To find the IP, you must navigate deeper down three more nested layers:
#             1. Find and open the key: "ietf-ip:ipv4"
#             2. Inside it, find the key: "address" (Warning: This is another list '[' at line 17!)
#             3. Step into slot 0 of the address list.
#             4. Read the final key named: "ip" ("192.168.91.130"). Target B locked.
# ======================================================================================


# CONSTRUCT DataExtractionLogic:
#     METHOD parse_cisco_model():
#         STEP 1: Point a temporary variable to the list inside "ietf-interfaces:interfaces" -> "interface"
#         STEP 2: Extract the "name" field from the first item (Index 0) of that list and print it out.
#         STEP 3: Drill down into the "ietf-ip:ipv4" -> "address" path from that same item.
#         STEP 4: Extract the final "ip" field value and print it out.



# ======================================================================================
# RELOAD BLUEPRINT: STEP 5 STRUCTURED PSEUDOCODE FORGE
# ======================================================================================
# 1. ENVIRONMENT STATUS:
#    - File: restconf_recon.py (Inside directory: 6_restconf_data_model_recon)
#    - State: Mock JSON data payload is saved and stable on lines 1-27.
#
# 2. IMMEDIATE GOAL:
#    - Take the wheel at line 32 and write out your custom structured pseudocode
#      using plain English mixed with programmatic formatting.
#    - Purpose: Step-by-step navigation of the nested JSON dictionaries and lists
#      to extract and print "name" and "ip".
#
# 3. NESTED LOGIC CHEAT SHEET FOR YOUR AFTERNOON DRAFT:
#    - Variable Name: mock_restconf_payload
#      -> Step 1: Open dictionary key "ietf-interfaces:interfaces"
#      -> Step 2: Open dictionary key "interface"
#      -> Step 3: Access list item at index position 0
#      -> Step 4: Extract "name" value
#      -> Step 5: Navigate down "ietf-ip:ipv4" -> "address" -> index 0 -> "ip"
# ======================================================================================



# CONSTRUCT MultiInterfaceExtractor:
#     METHOD parse_payload():
#         # Step 1: Lock down a shortcut path to the main interface list container
#         SET interface_list = mock_restconf_payload["ietf-interfaces:interfaces"]["interface"]
#
#         # Step 2: Target the first interface item (Index 0)
#         SET first_interface = interface_list[0]
#         PRINT first_interface["name"]
#         PRINT first_interface["ietf-ip:ipv4"]["address"][0]["ip"]
#
#         # Step 3: Target the second interface item (Index 1)
#         SET second_interface = interface_list[1]
#         PRINT second_interface["name"]