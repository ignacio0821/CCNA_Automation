# FILE: restconf_recon_OpenConfig.py
# DESCRIPTION: Production-Grade RESTCONF OpenConfig Consensus Data Model Telemetry Ingestion

# Canonical Cloud-Operator Driven Interface Target
URL = f"https://{ROUTER_IP}/restconf/data/openconfig-interfaces:interfaces/interface=GigabitEthernet1"

# Target Schema Navigation Path for Extraction
# response.json() structure traversal:
# ip_address = data["openconfig-interfaces:interfaces"]["interface"][0]["config"]["name"]
