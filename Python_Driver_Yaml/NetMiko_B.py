from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

# Define the connection parameters matching your live CML state
router_profile = {
    "device_type": "cisco_ios",
    "host": "192.168.91.130",  # Your exact live DHCP IP
    "username": "admin",
    "password": "Cisco123",
}

try:
    print(f"Initiating programmatic secure handshake to {router_profile['host']}...")

    # Open the encrypted transport tunnel safely
    with ConnectHandler(**router_profile) as connection:

        # Execute command and instantly return a structured Python data structure
        print("Executing operational data gathering command...")
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

  except NetmikoTimeoutException:
      print(f"❌ [CRITICAL ERROR]: Connection timed out to host {router_profile['host']}. Check routing topology.")
  except NetmikoAuthenticationException:
      print("❌ [CRITICAL ERROR]: Authentication failed. Verify credentials in router_profile mapping.")
  except Exception as e:
      print(f"❌ [UNEXPECTED ERROR]: {str(e)}")
