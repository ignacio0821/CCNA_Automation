import requests
import json
# Executable from blank memory core

# Endpoint Construction (The Interface URI Stack)
url = "https://cisco.com/restconf/data"

# The Strict RESTCONF Header Matrix
headers = {
    "Accept": "application/yang-data+json",          # Explicitly requesting YANG Data Format
    "Content-Type": "application/yang-data+json",    # Explicitly defining the payload Format
}

# The Direct Authentication Pointer
auth = ("developer", "Cisco123!")

# Live Execution Call
payload = {"ietf-interfaces:interface": {"name": "Loopback99"}}
response = requests.post(url, headers=headers, auth=auth, json=payload, verify=False)