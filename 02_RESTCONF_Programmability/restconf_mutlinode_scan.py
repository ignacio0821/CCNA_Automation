import requests
import urllib3

# Suppress insecure HTTPS warning outputs on self-signed sandbox certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# MASTER PRODUCTION INVENTORY ARRAY
LAB_INFRASTRUCTURE_CLUSTER = [
    {
        "hostname": "Core-01",
        "bridge_host": "192.168.91.132",
        "internal_ip": "10.255.0.11",
        "role": "Core"
    },
    {
        "hostname": "Core-02",
        "bridge_host": "192.168.91.135",
        "internal_ip": "10.255.0.12",
        "role": "Core"
    },
    {
        "hostname": "Edge-01",
        "bridge_host": "192.168.91.134",
        "internal_ip": "10.255.0.21",
        "role": "Edge"
    },
    {
        "hostname": "Edge-02",
        "bridge_host": "192.168.91.136",
        "internal_ip": "10.255.0.22",
        "role": "Edge"
    }
]


def execute_cluster_telemetry_audit():
    # RFC 8040 Strict Media Configuration
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json"
    }

    # Priv-15 Authentication Target Bounds
    auth_credentials = ("admin", "Cisco123")

    # Canonical YANG Module Path targeting the IOS-XE Native Root datastore Container
    target_path = "/restconf/data/Cisco-IOS-XE-native:native"

    print(f"[*] Initializing Multi-Node Telemetry Audit across {len(LAB_INFRASTRUCTURE_CLUSTER)} devices...")
    print("=" * 80)

    for device in LAB_INFRASTRUCTURE_CLUSTER:
        url = f"https://{device['bridge_host']}:443{target_path}"
        print(f"[>] Querying [{device['hostname']}] ({device['role']}) via bridge path: {device['bridge_host']}...")

        try:
            response = requests.get(
                url=url,
                headers=headers,
                auth=auth_credentials,
                timeout=4,
                verify=False
            )

            # Structural Response Code Evaluation
            if response.status_code == 200:
                payload_length = len(response.text)
                print(f"    [+] SUCCESS: Status 200 OK")
                print(f"    [+] Telemetry Stream Content Size: {payload_length} characters")
            else:
                print(f"    [-] ERROR: Target Node rejected request. HTTP Code: {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"    [-] FAILURE: Connection timed out. Node might be initializing or unreachable.")
        except requests.exceptions.RequestException as error_trace:
            print(f"    [-] CRITICAL: Network pipeline failure: {error_trace}")

        print("-" * 80)

    print("[*] Multi-Node Cluster Telemetry Audit Finished.")


if __name__ == "__main__":
    execute_cluster_telemetry_audit()
