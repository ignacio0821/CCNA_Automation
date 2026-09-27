{
  "ietf-interfaces:interfaces": {    <-- [Step 4: Top-Level Parent Key]
    "interface": [                     <-- [The Nested List / Array]
      {
        "name": "GigabitEthernet1",
        "description": "MANAGEMENT INTERFACE",
        "enabled": true,
        "ietf-ip:ipv4": {
          "address": [
            {
              "ip": "10.10.20.48",
              "netmask": "255.255.255.0"
            }
          ]
        }
      }
    ]
  }
}


curl -k -X GET "https://192.168.91" \
     -H "Accept: application/yang-data+json" \
     -u "sysadmin:Cisco123"
