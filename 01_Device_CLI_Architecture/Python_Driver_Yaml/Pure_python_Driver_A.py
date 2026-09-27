# Executable from blank memory core

import yaml
import json

def process_network_matrix(file_path):
    # Intentional execution check: open file stream securely
    try:
        with open(file_path, "r") as stream:
            # safe_load blocks arbitrary code execution vulnerabilities
            topology_data = yaml.safe_load(stream)
    except FileNotFoundError:
        return "CRITICAL ERROR: Topology schema asset target missing."

    inventory = topology_data.get("infrastructure_inventory", {})
    routers = inventory.get("backbone_routers", [])

    print(f"=== INVENTORY VERIFICATION: {len(routers)} CORE ROUTERS DETECTED ===\n")

    # Step through structural dictionary hierarchy
    for router in routers:
        hostname = router.get("hostname")
        mgmt_ip = router.get("mgmt_ip")
        interfaces = router.get("interfaces", [])

        print(f"HOST: {hostname} | MANAGEMENT PLANE: {mgmt_ip}")

        # Parse multi-path array parameters
        for current_interface in interfaces:
            int_name = current_interface.get("name")
            ip_addr = current_interface.get("ip_address")
            metric_value = current_interface.get("metric")

            # Defensive verification: Ensure metric isn't a hidden string type
            if not isinstance(metric_value, int):
                print(f"  [!] SYNTAX ALERT: Mixed type metric mismatch on {int_name}!")
                continue

            # Identify traffic engineering priority
            path_role = "PRIMARY" if metric_value == 10 else "BACKUP"

            print(f"   -> Interface: {int_name} | IP: {ip_addr:<18} | Metric: {metric_value} [{path_role}]")
        print("_"* 65)


# Example invocation for local system test loops
if __name__ == "__main__":
    process_network_matrix("topology.yaml")
