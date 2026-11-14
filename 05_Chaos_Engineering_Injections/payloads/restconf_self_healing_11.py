import json
import os
from pathlib import Path
import requests
import urllib3
import yaml

# Suppress self-signed certificate warnings for local CML testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DriftDetectionError(Exception):
    """Raised when a configuration push fails validation and requires self-healing."""

    pass


def load_golden_baseline(yaml_path: Path) -> dict:
    """Reads the trusted golden YAML file and converts it to an IOS-XE YANG payload."""
    with yaml_path.open("r", encoding="utf-8") as file:
        intent_data = yaml.safe_load(file)

    target = intent_data["target_interface"]
    state = target["configuration_state"]
    ip_cfg = state["ip_assignment"]

    return {
        "Cisco-IOS-XE-native:GigabitEthernet": {
            "name": str(target["slot_id"]),
            "description": state["description"],
            "ip": {
                "address": {
                    "primary": {
                        "address": ip_cfg["ipv4_address"],
                        "mask": ip_cfg["subnet_mask"],
                    }
                }
            },
        }
    }


def remediate_to_golden_baseline(
    host: str, username: str, password: str, golden_yaml: Path
) -> None:
    """Closed-loop remediation engine: enforces trusted state via HTTP PATCH and saves NVRAM."""
    print(
        "\n[SELF-HEALING] Intercepted fault. Initiating automated HTTP PATCH rollback..."
    )
    golden_payload = load_golden_baseline(golden_yaml)
    interface_id = golden_payload["Cisco-IOS-XE-native:GigabitEthernet"]["name"]

    url = f"https://{host}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={interface_id}"
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json",
    }

    try:
        # 1. Execute HTTP PATCH to merge/enforce golden YAML state
        patch_resp = requests.patch(
            url,
            auth=(username, password),
            headers=headers,
            json=golden_payload,
            verify=False,
            timeout=10,
        )

        if patch_resp.status_code in (200, 201, 204):
            print(
                f"  -> [HEALED] HTTP {patch_resp.status_code}: Golden YAML baseline re-applied via PATCH."
            )

            # 2. Persist healed configuration to NVRAM via save-config RPC
            rpc_url = f"https://{host}/restconf/operations/cisco-ia:save-config"
            rpc_resp = requests.post(
                rpc_url,
                auth=(username, password),
                headers=headers,
                json={},
                verify=False,
                timeout=15,
            )
            if rpc_resp.status_code in (200, 204):
                print(
                    f"  -> [PERSISTED] HTTP {rpc_resp.status_code}: Healed state written to NVRAM."
                )
        else:
            print(
                f"  -> [CRITICAL] Self-healing PATCH failed (HTTP {patch_resp.status_code}): {patch_resp.text}"
            )

    except requests.exceptions.RequestException as err:
        print(f"  -> [CRITICAL] Network unreachable during self-healing loop: {err}")


def run_closed_loop_pipeline() -> None:
    host = os.getenv("ROUTER_HOST", "192.168.91.135")
    username = os.getenv("ROUTER_USER", "admin")
    password = os.getenv("ROUTER_PASS")

    if not password:
        print("[ABORT] Set ROUTER_PASS in your PyCharm Run Configuration first.")
        return

    assert password is not None

    # Resolve golden YAML path relative to 05_Chaos_Engineering_Injections/payloads/
    project_root = Path(__file__).resolve().parents[2]
    golden_yaml_path = (
        project_root / "02_RESTCONF_Programmability" / "interface_provision_2.yaml"
    )

    url = f"https://{host}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=2"
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json",
    }

    # Simulated corrupted state push (from Step 10 Chaos Vector)
    corrupted_payload = {
        "Cisco-IOS-XE-native:GigabitEthernet": {
            "name": "2",
            "ip": {
                "address": {
                    "primary": {
                        "address": "999.999.999.999",
                        "mask": "255.255.255.0",
                    }
                }
            },
        }
    }

    print("=" * 75)
    print("STARTING STEP 11: CLOSED-LOOP SELF-HEALING PIPELINE")
    print("=" * 75)

    try:
        print("[STEP 1] Attempting state push to Core-02...")
        response = requests.put(
            url,
            auth=(username, password),
            headers=headers,
            json=corrupted_payload,
            verify=False,
            timeout=10,
        )

        if response.status_code not in (200, 201, 204):
            raise DriftDetectionError(
                f"Router rejected state push with HTTP {response.status_code}"
            )

        print("[SUCCESS] State push applied cleanly without drift.")

    except (DriftDetectionError, requests.exceptions.RequestException) as fault:
        print(f"[FAULT DETECTED] {fault}")
        remediate_to_golden_baseline(host, username, password, golden_yaml_path)

    print("\n" + "=" * 75)
    print("[COMPLETE] CLOSED-LOOP SELF-HEALING CYCLE FINISHED (Exit Code 0)")
    print("=" * 75)


if __name__ == "__main__":
    run_closed_loop_pipeline()
