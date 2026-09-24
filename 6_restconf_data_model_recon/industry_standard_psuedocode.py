# INITIALIZE string constant ENDPOINT_TARGET
# INITIALIZE dictionary headers configuration
# INITIALIZE local variable name_payload
#
# TRY
#     EXECUTE secure network HTTP GET to ENDPOINT_TARGET with headers
#     PARSE raw response string text format into JSON dictionary object
#
#     // Step 6a: Navigate data tree boundary safely using strict keys
#     EXTRACT list element interface_list FROM JSON_data["Cisco-IOS-XE-native:interface"]["GigabitEthernet"]
#
#     PRINT Report Header formatting strings
#
#     // Step 6b: Iterate through list elements sequentially
#     FOR EACH device_record IN interface_list DO
#
#         EXTRACT interface_name FROM device_record["name"]
#
#         // Step 6c: Identify administrative state using key membership detection
#         IF key "shutdown" EXISTS WITHIN device_record THEN
#             SET administrative_status = "DOWN"
#         ELSE
#             SET administrative_status = "UP"
#         ENDIF
#
#         // Step 6d: Safely drill downstream into network layer dictionaries
#         EXTRACT ip_container FROM device_record USING safe lookup (.get)
#         EXTRACT address_container FROM ip_container USING safe lookup (.get)
#
#         // Step 6e: Conditional validation tree for IP assignment architecture
#         IF key "dhcp" EXISTS WITHIN address_container THEN
#             SET target_ip = "DYNAMIC (DHCP Assigned)"
#             SET target_mask = "DYNAMIC (DHCP Assigned)"
#         ELSE IF key "primary" EXISTS WITHIN address_container THEN
#             EXTRACT primary_record FROM address_container USING safe lookup
#             SET target_ip = primary_record["address"]
#             SET target_mask = primary_record["netmask"]
#         ELSE
#             SET target_ip = "UNCONFIGURED (Layer-2 / Disabled)"
#             SET target_mask = "UNCONFIGURED"
#         ENDIF
#
#         // Step 6f: Emit output card profile metrics
#         PRINT interface_name, administrative_status, target_ip, target_mask
#
#     ENDFOR
#
#     PRINT Report Footer formatting strings
#
# EXCEPT NetworkConnectionError THEN
#     LOG "Transport pipeline failed. Device unreachable."
#     HALT execution
# EXCEPT KeyLookupError THEN
#     LOG "YANG schema change detected. Payload malformed."
#     HALT execution
# ENDTRY
#