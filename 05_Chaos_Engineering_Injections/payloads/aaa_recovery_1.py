import sys
import os
from dotenv import load_dotenv
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

load_dotenv()

# 1. Target Parameters (Modify values inline for your local CML topology)
device = {
    "device_type": "cisco_ios",
    "host": os.getenv("EDGE01_HOST", "198.51.100.1"),
    "username": os.getenv("CML_USERNAME", "netops_admin"),
    "password": os.environ["CML_PASSWORD"],
    "secret": os.environ["CML_SECRET"],
    "fast_cli": False,  # Keep False to ensure step-by-step buffer processing during lock state
}

# 2. Recovery Commands to Undo the Hallucinated State
recovery_commands = ["aaa authorization exec default local", "do write memory"]

print("[*] Initiating emergency recovery loop for Edge-01...")

try:
    # Establish connection before the active session fully times out or drops
    with ConnectHandler(**device) as net_connect:
        net_connect.enable()

        print("[+] Connection verified. Pushing rescue commands to buffer...")
        # send_config_set handles config t entry and exit automatically
        output = net_connect.send_config_set(recovery_commands)

        print("\n--- DEVICE OUTPUT ---")
        print(output)
        print("---------------------\n")

        # Post-execution verification check
        verification = net_connect.send_command("show run | include aaa authorization")
        print(f"[+] Active AAA Configuration State:\n{verification}")

        if "exec default local" in verification:
            print(
                "[SUCCESS] AAA executive authorization state restored programmatically."
            )
        else:
            print(
                "[FAIL] Command injected but verification check failed to read state change."
            )

except (NetmikoTimeoutException, NetmikoAuthenticationException) as auth_err:
    print(f"[CRITICAL FAILURE] Blocked at AAA authentication level: {auth_err}")
    print(
        "[!] ACTION REQUIRED: Do not close any open terminal windows to this node. Use the CML Console port directly."
    )
except Exception as e:
    print(f"[UNKNOWN ERROR] Execution stalled: {e}")
    sys.exit(1)
