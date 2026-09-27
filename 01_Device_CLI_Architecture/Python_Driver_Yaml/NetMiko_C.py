import yaml
from pathlib import Path
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

# 1. Define defensive, absolute or relative tracking paths to your configuration file
CONFIG_PATH = Path(__file__).parent / "config.yaml"

try:
    print(f"Opening secure tracking pointer to structural layout: {CONFIG_PATH.name}...")

    # 2. Open the file context manager stream and extract raw structured schema safely
    with open(CONFIG_PATH, "r") as file_stream:
        config_data = yaml.safe_load(file_stream)

    print("YAML schema compiled successfully into local dictionary namespace.")

    # 3. Programmatically map the deep nested objects directly out of the dictionary
    router_profile = config_data["target_nodes"]["core_router_01"]
    audit_params = config_data["audit_parameters"]

    print(f"Initiating programmatic secure handshake to decoupled host: {router_profile['host']}...")

    # 4. Open the encrypted transport tunnel utilizing keyword argument unpacking (**)
    with ConnectHandler(**router_profile) as connection:

        print(f"Executing operational command template: '{audit_params['target_command']}'...")
        structured_output = connection.send_command(audit_params["target_command"], use_textfsm=True)

        print("\n--- [Dynamic Data Payload Extraction Successful] ---")

        if isinstance(structured_output, list):
            print(
                f"\nActive Interfaces Audit ({audit_params['required_status'].upper()}/{audit_params['required_protocol'].upper()}):")
            for interface in structured_output:
                if isinstance(interface, dict):
                    # Leverage your external parameters directly inside your loop gate logic
                    if (interface.get("status") == audit_params["required_status"] and
                            interface.get("protocol") == audit_params["required_protocol"]):
                        print(f"  📌 Interface: {interface.get('interface')} -> IP: {interface.get('ip_address')}")
        else:
            print("❌ [ERROR]: TextFSM failed to return structured data structure.")

except FileNotFoundError:
    print(f"❌ [CRITICAL CONFIG ERROR]: Could not find file configuration layout at path: {CONFIG_PATH}")
except yaml.YAMLError as yaml_err:
    print(f"❌ [CRITICAL SYNTAX ERROR]: Failed to parse YAML file. Check whitespace layout structure:\n{yaml_err}")
except NetmikoTimeoutException:
    print(f"❌ [NETWORK ERROR]: Connection timed out to host {router_profile.get('host')}.")
except NetmikoAuthenticationException:
    print("❌ [NETWORK ERROR]: Authentication failed. Check your credential maps inside config.yaml.")
except Exception as e:
    print(f"❌ [UNEXPECTED RUNTIME ERROR]: {str(e)}")
