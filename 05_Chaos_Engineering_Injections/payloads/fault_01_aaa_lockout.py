# ==============================================================================
# INJECTION PROFILE: fault_01_aaa_lockout.py
# SILO:             05_Chaos_Engineering_Injections/payloads
# FAULT VECTOR:     Control Plane AAA Authentication/Authorization Failure
# TARGET PROTOCOL:  RESTCONF HTTP 401 Unauthorized State
# ==============================================================================

"""
TEST PARADIGM & SIMULATION INSTRUCTIONS:

1. TARGET LIVE SANDBOX COGNITION:
   - Cisco Modeling Labs (CML) Endpoint: 192.168.91.132 (Edge-01)

2. LIVE BARE-METAL INJECTION COMMANDS (EXECUTE ON SWITCH TERMINAL):
   - Access global configuration tier:
     Edge-01# configure terminal
   - Strip away virtual terminal execution permission mappings:
     Edge-01(config)# no aaa authorization exec default local

3. EXPECTED AUTOMATION CORE TELEMETRY CRASH RESULT:
   - Synchronous requests session drops during authorization checks.
   - HTTP Server response daemon immediately returns status code: 401 Unauthorized.
   - Idempotent loop must catch requests.exceptions.HTTPError, log the exact 401
     event parameters cleanly, bypass code block execution, and advance to next node.
"""

# Hardened verification string to confirm fault deployment during local mock logs
FAULT_METADATA = {
    "vector_id": "CHOS_MONK_01",
    "target_ios_xe_service": "RESTCONF-DMI-DAEMON",
    "simulated_http_fault_trigger": 401,
    "recovery_revert_command": "aaa authorization exec default local"
}

def verify_fault_relevance():
    print(f"[!] INJECTION RUNNING: Verifying resilience against fault {FAULT_METADATA['vector_id']}.")
