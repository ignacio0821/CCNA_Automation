import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://192.168.91.129/restconf/data/ietf-interfaces:interfaces"
auth_profile = HTTPBasicAuth("admin", "Cisco123")
header_profile = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

try:
    response = requests.get(
        url=URL,
        auth=auth_profile,
        headers=header_profile,
        verify=False
    )
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Error Code: {response.status_code}")
except Exception as e:
    print(f"Connection Failed: {e}")
