import os
from dotenv import load_dotenv
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

load_dotenv()

# Define the connection parameters matching your live CML state
router_profile = {
    "device_type": "cisco_ios",
    "host": os.getenv("NETMIKO_A_HOST", "198.51.100.10"),
    "username": os.getenv("CML_USERNAME", "netops_admin"),
    "password": os.environ["CML_PASSWORD"],
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
                    if interface.get("status") == "up" and interface.get("protocol") == "up":
                        print(f"  -> Interface: {interface.get('interface')} -> IP: {interface.get('ip_address')}")
        else:
            print("X [ERROR]: TextFSM failed to return structured data. Expected a list structure.")

except NetmikoTimeoutException:
    print(f"X [CRITICAL ERROR]: Connection timed out to host {router_profile['host']}. Check routing topology.")
except NetmikoAuthenticationException:
    print("X [CRITICAL ERROR]: Authentication failed. Verify credentials in router_profile mapping.")
except Exception as e:
    print(f"X [UNEXPECTED ERROR]: {str(e)}")

