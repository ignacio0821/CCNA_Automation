import yaml
from pathlib import Path
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

# Define absolute tracking path to your updated configuration file
CONFIG_PATH = Path(__file__).parent / "config.yaml"

try:
    # 1. Ingest the inventory schema safely
    with open(CONFIG_PATH, "r") as file_stream:
        config_data = yaml.safe_load(file_stream)

    device_list = config_data.get("target_nodes", [])
    audit_params = config_data.get("audit_parameters", {})

    print(f"Loaded {len(device_list)} target nodes from inventory asset structure.\n")

    # 2. Iterate through each target device sequentially
    for device in device_list:
        hostname = device.get("hostname", "Unknown_Host")
        print(f"==================================================")
        print(f"🚀 Starting Automation Track for Node: {hostname}")
        print(f"==================================================")

        # Clean the dictionary to pass safely to Netmiko by removing custom metadata
        connection_profile = {
            "device_type": device.get("device_type"),
            "host": device.get("host"),
            "username": device.get("username"),
            "password": device.get("password"),
        }

        # 3. Inner defensive try block ensures single-node errors don't crash the loop
        try:
            print(f"Initiating programmatic handshake to {connection_profile['host']}...")

            with ConnectHandler(**connection_profile) as connection:
                print(f"Executing operational audit: '{audit_params['target_command']}'")
                structured_output = connection.send_command(audit_params["target_command"], use_textfsm=True)

                print(f"--- [{hostname} Data Extraction Successful] ---")

                if isinstance(structured_output, list):
                    print(
                        f"Active Interfaces ({audit_params['required_status'].upper()}/{audit_params['required_protocol'].upper()}):")
                    for interface in structured_output:
                        if isinstance(interface, dict):
                            if (interface.get("status") == audit_params["required_status"] and
                                    interface.get("protocol") == audit_params["required_protocol"]):
                                print(
                                    f"  📌 Interface: {interface.get('interface')} -> IP: {interface.get('ip_address')}")
                else:
                    print("❌ [ERROR]: TextFSM failed to return expected list structure.")

        except NetmikoTimeoutException:
            print(
                f"❌ [NODE ERROR]: Connection timed out to {hostname} ({connection_profile['host']}). Skipping to next asset.")
        except NetmikoAuthenticationException:
            print(f"❌ [NODE ERROR]: Auth failed for {hostname}. Verify credentials. Skipping to next asset.")
        except Exception as node_err:
            print(f"❌ [NODE ERROR]: Unexpected error on {hostname}: {str(node_err)}. Skipping to next asset.")

        print(f"🏁 Finished processing for node: {hostname}\n")

except FileNotFoundError:
    print(f"❌ [CRITICAL CONFIG ERROR]: Could not find file layout at path: {CONFIG_PATH}")
except yaml.YAMLError as yaml_err:
    print(f"❌ [CRITICAL SYNTAX ERROR]: Failed to parse configuration YAML:\n{yaml_err}")
except Exception as e:
    print(f"❌ [GLOBAL CRITICAL ERROR]: {str(e)}")
