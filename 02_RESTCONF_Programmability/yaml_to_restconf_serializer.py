import json
import yaml
from pathlib import Path


def serialize_yaml_to_json(yaml_filepath: str) -> str:
    """Ingests interface_provision_2.yaml, maps it to IOS-XE YANG, and outputs JSON."""
    path = Path(yaml_filepath)

    try:
        # 1. Read the raw YAML file from disk
        with path.open("r", encoding="utf-8") as file:
            intent_data = yaml.safe_load(file)

        # 2. Extract your custom intent parameters
        target = intent_data["target_interface"]
        state = target["configuration_state"]
        ip_cfg = state["ip_assignment"]

        # 3. Map custom YAML keys into strict Cisco IOS-XE YANG structure
        yang_payload = {
            "Cisco-IOS-XE-native:interface": {
                target["type"]: [
                    {
                        "name": str(target["slot_id"]),
                        "description": state["description"],
                        "ip": {
                            "address": {
                                "primary": {
                                    "address": ip_cfg["ipv4_address"],
                                    "mask": ip_cfg["subnet_mask"]
                                }
                            }
                        }
                    }
                ]
            }
        }

        # 4. Serialize the Python dictionary into a formatted RESTCONF JSON string
        return json.dumps(yang_payload, indent=2)

    except FileNotFoundError:
        return f"[ERROR] Could not locate YAML file at: {yaml_filepath}"
    except yaml.YAMLError as exc:
        return f"[YAML SYNTAX ERROR] Failed to parse YAML structure: {exc}"
    except KeyError as missing_key:
        return f"[SCHEMA ERROR] Missing required key in YAML draft: {missing_key}"


if __name__ == "__main__":
    # Targets your exact file inside 02_RESTCONF_Programmability
    json_output = serialize_yaml_to_json("interface_provision_2.yaml")
    print("=== GENERATED CISCO IOS-XE RESTCONF JSON PAYLOAD ===")
    print(json_output)
