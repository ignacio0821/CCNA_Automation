import os
import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

# CML Cluster Hypervisor Endpoint Parameters
CML_HOST = "192.168.91.129"  # Your central CML controller IP string
LAB_ID = "/lab/2bccb28d-5099-4f89-9662-ddfe1fc4688e"
NODE_ID = "972429c3-f99d-4b68-8b96-4d01f2283e38"

cml_auth = (os.getenv("CML_USER"), os.getenv("CML_PASS"))
cml_headers = {"Content-Type": "application/json"}

# Target the CML console injection endpoint for the virtual serial line
console_url = f"https://{CML_HOST}/api/v0/labs/{LAB_ID}/nodes/{NODE_ID}/console"

print("[>] Launching programmatic Out-of-Band Hypervisor break-in...")

# Serial command payload to force configuration healing without network AAA checks
repair_payload = "\r\nconfigure terminal\r\naaa authorization exec default local\r\nend\r\n"

try:
    response = requests.put(
        url=console_url,
        headers=cml_headers,
        data=repair_payload,
        auth=cml_auth,
        verify=False,
        timeout=5.0
    )
    if response.status_code == 200:
        print("[++] SUCCESS: CML Hypervisor programmatically healed the control plane over virtual serial connection!")
    else:
        print(f"[-] Hypervisor rejected command injection. Code: {response.status_code}")

except requests.exceptions.RequestException as err:
    print(f"[-] Infrastructure injection failed: {err}")
