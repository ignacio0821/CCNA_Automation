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
    # Open the encrypted transport tunnel
    connection = ConnectHandler(**router_profile)

    # Execute the operational data gathering command
    output = connection.send_command("show ip interface brief")

    print("\n--- [Data Payload Extraction Successful] ---")
    print(output)

    # Gracefully drop the session
    connection.disconnect()

except NetmikoTimeoutException:
    print(
        "\n[!] Error: Unable to reach the control plane. Check your workstation routing table."
    )
except NetmikoAuthenticationException:
    print("\n[!] Error: The AAA engine rejected the configured credentials.")
except Exception as e:
    print(f"\n[!] Unexpected Operational Fault: {e}")
