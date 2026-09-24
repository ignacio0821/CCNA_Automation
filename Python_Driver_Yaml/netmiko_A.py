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
    # Open the encrypted transport tunnel
    connection = ConnectHandler(**router_profile)

    # Execute the operational data gathering command
    output = connection.send_command("show ip interface brief")

    print("\n--- [Data Payload Extraction Successful] ---")
    print(output)

    # Gracefully drop the session
    connection.disconnect()

except NetmikoTimeoutException:
    print("\n[!] Error: Unable to reach the control plane. Check your workstation routing table.")
except NetmikoAuthenticationException:
    print("\n[!] Error: The AAA engine rejected the configured credentials.")
except Exception as e:
    print(f"\n[!] Unexpected Operational Fault: {e}")
