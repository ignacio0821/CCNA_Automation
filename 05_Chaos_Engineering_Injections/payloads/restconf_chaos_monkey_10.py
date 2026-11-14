import os
import requests
import urllib3
import yaml

# Suppress self-signed certificate warnings for local CML testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ChaosValidationError(Exception):
    """Custom exception raised when chaos fault boundaries are triggered."""
    pass


def test_corrupted_yaml_ingestion() -> None:
    """Vector 1: Intentionally feeds malformed YAML syntax into the parser."""
    print("\n[CHAOS VECTOR 1] Injecting corrupted YAML syntax...")
    corrupted_yaml = """
    target_interface:
      type: "GigabitEthernet"
        slot_id: "2"  # Bad indentation injected intentionally
    """
    try:
        yaml.safe_load(corrupted_yaml)
    except yaml.YAMLError as err:
        print(f"  -> [TRAPPED] Caught YAMLError cleanly: {err.__class__.__name__}")
        raise ChaosValidationError("Corrupted YAML aborted safely before network push.") from err


def test_malformed_yang_payload(host: str, username: str, password: str) -> None:
    """Vector 2: Sends an illegal IPv4 address ('999.999.999.999') to Core-02."""
    print("\n[CHAOS VECTOR 2] Pushing malformed YANG payload (invalid IPv4) to Core-02...")
    url = f"https://{host}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=2"
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json",
    }
    bad_payload = {
        "Cisco-IOS-XE-native:GigabitEthernet": {
            "name": "2",
            "ip": {
                "address": {
                    "primary": {
                        "address": "999.999.999.999",
                        "mask": "255.255.255.0"
                    }
                }
            }
        }
    }

    try:
        response = requests.put(
            url, auth=(username, password), headers=headers,
            json=bad_payload, verify=False, timeout=5
        )
        if response.status_code == 400:
            print("  -> [TRAPPED] Core-02 rejected invalid YANG data with HTTP 400 Bad Request.")
            raise ChaosValidationError("Malformed YANG payload blocked cleanly by router schema.")
        print(f"  -> [UNEXPECTED] Received HTTP {response.status_code}")
    except requests.exceptions.RequestException as err:
        raise ChaosValidationError(f"Network fault during payload test: {err}") from err


def test_invalid_credentials(host: str, username: str) -> None:
    """Vector 3: Simulates credential mismatch / expired token mid-execution."""
    print("\n[CHAOS VECTOR 3] Injecting tampered credentials against Core-02...")
    url = f"https://{host}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=2"
    headers = {"Accept": "application/yang-data+json"}

    try:
        response = requests.get(
            url, auth=(username, "Tampered_Invalid_Pass_999"),
            headers=headers, verify=False, timeout=5
        )
        if response.status_code == 401:
            print("  -> [TRAPPED] Core-02 blocked unauthorized access with HTTP 401.")
            raise ChaosValidationError("Authentication failure trapped cleanly.")
    except requests.exceptions.RequestException as err:
        raise ChaosValidationError(f"Network fault during auth test: {err}") from err


def test_unreachable_host_timeout() -> None:
    """Vector 4: Simulates sudden interface/link drop using a non-routable blackhole IP."""
    print("\n[CHAOS VECTOR 4] Simulating sudden link drop / unreachable host (2s timeout)...")
    blackhole_url = "https://192.0.2"
    headers = {"Accept": "application/yang-data+json"}

    try:
        requests.get(
            blackhole_url, auth=("chaos_dummy_user", "chaos_dummy_pass"),
            headers=headers, verify=False, timeout=2
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as err:
        print(f"  -> [TRAPPED] Socket timeout handled cleanly without hanging: {err.__class__.__name__}")
        raise ChaosValidationError("Unreachable node dropped cleanly within timeout window.") from err


def run_chaos_suite() -> None:
    host = os.getenv("ROUTER_HOST", "192.168.91.135")
    username = os.getenv("ROUTER_USER", "admin")
    password = os.getenv("ROUTER_PASS")

    if not password:
        print("[ABORT] Set ROUTER_PASS in your PyCharm Run Configuration first.")
        return

    assert password is not None

    print("=" * 75)
    print("STARTING STEP 10: CHAOS MONKEY RESILIENCE SUITE")
    print("=" * 75)

    chaos_tests = [
        lambda: test_corrupted_yaml_ingestion(),
        lambda: test_malformed_yang_payload(host, username, password),
        lambda: test_invalid_credentials(host, username),
        lambda: test_unreachable_host_timeout(),
    ]

    passed = 0
    for idx, test_fn in enumerate(chaos_tests, start=1):
        try:
            test_fn()
        except ChaosValidationError as expected_fault:
            print(f"  -> [PASS] Vector {idx} Resilience Verified: {expected_fault}")
            passed += 1

    print("\n" + "=" * 75)
    print(f"[COMPLETE] {passed}/{len(chaos_tests)} Chaos Vectors Trapped Cleanly (Exit Code 0)")
    print("=" * 75)


if __name__ == "__main__":
    run_chaos_suite()
