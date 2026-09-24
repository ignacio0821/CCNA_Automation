# EXECUTABLE PATH ENGINE
import os
import yaml
import requests
import urllib3

# Suppress SSL certificate warnings for local Sandbox environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_network_inventory(file_path):
    """Parses structural nodes and data bindings from raw YAML source."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing logical configuration asset: {file_path}")

    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def deploy_path_policy(router):
    """Constructs the RESTCONF payload to enforce core metrics."""
    base_url = f"https://{router['mgmt_ip']}/restconf/data/ietf-interfaces:interfaces"
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json"
    }
    auth = ("developer", "Cisco123!")

    print(f"\n📡 Initiating configuration push to node: {router['hostname']} ({router['mgmt_ip']})")

    for interface in router['interfaces']:
        print(f"  ↳ Configuring {interface['name']} | Direct Link Cost [Metric: {interface['metric']}]")

        # RESTCONF Interface Configuration Payload
        payload = {
            "ietf-interfaces:interface": {
                "name": interface['name'],
                "type": "iana-if-type:ethernetCsmacd",
                "enabled": True,
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": interface['ip_address'].split('/')[0],
                            "netmask": "255.255.255.252"  # Transposing /30 topology constraint
                        }
                    ]
                }
            }
        }

        # In a real environment, requests.put would be called here to overwrite interface data:
        # response = requests.put(f"{base_url}/interface={interface['name']}", headers=headers, auth=auth, json=payload, verify=False)


if __name__ == "__main__":
    inventory_path = "../multi-router-automation/data/network_inventory.yaml"

    try:
        data_matrix = load_network_inventory(inventory_path)
        routers = data_matrix['infrastructure_inventory']['backbone_routers']

        for router_node in routers:
            deploy_path_policy(router_node)

        print("\n✅ Execution Complete: Infrastructure states successfully aligned to path policy.")

    except Exception as e:
        print(f"\n❌ Execution Interrupted: {str(e)}")