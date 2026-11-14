# FILE: restconf_recon_IETF.py
# DESCRIPTION: Production-Grade RESTCONF IETF-Standard Data Model Telemetry Ingestion

# Canonical RFC 8040 Industry-Standard Interface Target
URL = f"https://{ROUTER_IP}/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1"

# Target Schema Navigation Path for Extraction
# response.json() structure traversal:
# ip_address = data["ietf-interfaces:interfaces"]["interface"][0]["ietf-ip:ipv4"]["address"][0]["ip"]
