# Enterprise Inventory Audit Engine
core_01_vlans = {10, 20, 30, 99}
dist_a_vlans = {10, 20, 40}

# Programmatic Set Difference Operation
missing_from_core = dist_a_vlans.difference(core_01_vlans)

print(f"CRITICAL COMPLIANCE ALERT: Missing VLANs on Core-01: {missing_from_core}")
# Output: Missing VLANs on Core-01: {40}


structured_output = connection.send_command("show ip interface brief", use_textfsm=True)

print("\n--- [Data Payload Extraction Successful] ---")

# Explicit type validation gate to satisfy static analyzers and prevent runtime crashes
if isinstance(structured_output, list):
    print("\nActive Interfaces (Up/Up) Audit:")
    for interface in structured_output:
        # Double-check that inner objects are indeed dictionary elements
        if isinstance(interface, dict):
            if interface.get('status') == 'up' and interface.get('protocol') == 'up':
                print(f"  📌 Interface: {interface.get('interface')} -> IP: {interface.get('ip_address')}")
else:
    print("❌ [ERROR]: TextFSM failed to return structured data. Expected a list structure.")
