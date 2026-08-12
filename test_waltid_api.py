#!/usr/bin/env python3
"""
walt.id REST API Test Suite (Python)
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

# Environment variable ports matching walt.id setup
ISSUER_PORT = os.getenv("ISSUER_API2_PORT", "7005")
VERIFIER_PORT = os.getenv("VERIFIER_API2_PORT", "7004")
WALLET_PORT = os.getenv("WALLET_API2_PORT", "7006")
HOST = os.getenv("HOST", "localhost")

MAX_RETRIES = 30
RETRY_INTERVAL = 2


def wait_for_service(url: str, service_name: str) -> bool:
    """Polls a service URL until it responds or timeout limit is reached."""
    print(f"[WAIT] Checking {service_name} at {url}...")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "waltid-pytest/1.0"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status in (200, 201, 404, 400):
                    print(f"  [+] {service_name} is READY! (HTTP {resp.status})")
                    return True
        except urllib.error.HTTPError as e:
            if e.code in (200, 201, 404, 400):
                print(f"  [+] {service_name} is READY! (HTTP {e.code})")
                return True
        except (urllib.error.URLError, TimeoutError, ConnectionRefusedError):
            pass

        print(f"  Attempt {attempt}/{MAX_RETRIES}: waiting {RETRY_INTERVAL}s...")
        time.sleep(RETRY_INTERVAL)

    print(f"[-] ERROR: {service_name} failed to respond within time limit.")
    sys.exit(1)


def test_create_wallet() -> str:
    """POST /wallet to create a new wallet and return walletId."""
    url = f"http://{HOST}:{WALLET_PORT}/wallet"
    print(f"\n[TEST 1] POST {url} (Create New Wallet)...")

    payload = json.dumps({}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "waltid-pytest/1.0"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            response_body = resp.read().decode("utf-8")
            data = json.loads(response_body)

            print(f"  HTTP Status: {status}")
            print(f"  Response Body: {json.dumps(data, indent=2)}")

            assert status == 201, f"Expected HTTP 201, got {status}"

            # Assert walletId exists
            wallet_id = data.get("walletId") or data.get("id")
            assert wallet_id is not None, "Response JSON missing 'walletId' field!"

            print(f"  [SUCCESS] Created Wallet ID: {wallet_id}")
            return str(wallet_id)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"  [-] HTTP Error {e.code}: {error_body}")
        sys.exit(1)


def test_create_key(wallet_id):
    """POST /wallet/{wallet_id}/keys/generate to create a new key."""
    url = f"http://{HOST}:{WALLET_PORT}/wallet/{wallet_id}/keys/generate"
    print(f"\n[TEST 2] POST {url} (Create New Key)...")

    payload = json.dumps({"backend": "jwk", "keyType": "Ed25519"}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "waltid-pytest/1.0"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            response_body = resp.read().decode("utf-8")
            data = json.loads(response_body)

            print(f"  HTTP Status: {status}")
            print(f"  Response Body: {json.dumps(data, indent=2)}")

            assert status == 201, f"Expected HTTP 201, got {status}"

            # Assert keyId exists
            key_id = data.get("keyId") or data.get("id")
            assert key_id is not None, "Response JSON missing 'keyId' field!"

            print(f"  [SUCCESS] Created Wallet Key ID: {key_id}")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"  [-] HTTP Error {e.code}: {error_body}")
        sys.exit(1)


def test_create_did(wallet_id):
    """POST /wallet/{wallet_id}/dids/create to create a new DID."""
    url = f"http://{HOST}:{WALLET_PORT}/wallet/{wallet_id}/dids/create"
    print(f"\n[TEST 3] POST {url} (Create New DID)...")

    payload = json.dumps({"method": "key"}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "waltid-pytest/1.0"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            response_body = resp.read().decode("utf-8")
            data = json.loads(response_body)

            print(f"  HTTP Status: {status}")
            print(f"  Response Body: {json.dumps(data, indent=2)}")

            assert status == 201, f"Expected HTTP 201, got {status}"

            # Assert 'did' exists
            did = data.get("did") or data.get("id")
            assert did is not None, "Response JSON missing 'did' field!"

            print(f"  [SUCCESS] Created Wallet DID: {did}")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"  [-] HTTP Error {e.code}: {error_body}")
        sys.exit(1)


def test_issuer_profile(profile_id):
    """GET /issuer2/profiles/{profile_id} to verify generated entity profile."""
    url = f"http://{HOST}:{ISSUER_PORT}/issuer2/profiles/{profile_id}"
    print(f"\n[TEST 4] GET {url} (Verify Custom Profile)...")
    try:
        with urllib.request.urlopen(url) as resp:
            status = resp.status
            data = json.loads(resp.read().decode("utf-8"))
            assert status == 200, f"Expected HTTP 200, got {status}"
            profile_name = data.get("name", profile_id)
            print(f"  [SUCCESS] Loaded Profile: {profile_name}")
    except urllib.error.HTTPError as e:
        print(f"  [-] HTTP Error {e.code}: {e.read().decode('utf-8')}")


def test_issuer_create_offers(profile_id):
    """POST /issuer2/credential-offers to create a new offer."""
    url = f"http://{HOST}:{ISSUER_PORT}/issuer2/credential-offers"
    print(f"\n[TEST 5] POST {url} (Create New Offer)...")

    payload = json.dumps(
        {
            "profileId": {profile_id},
            "authMethod": "PRE_AUTHORIZED",
            "runtimeOverrides": {
                "credentialData": {
                    "credentialSubject": {
                        "studentInfo": {
                            "firstName": "Jane",
                            "lastName": "Kim",
                            "birthday": "2000-01-01T00:00:00Z",
                            "gender": "Female",
                            "intake": 2019,
                            "school": "School of Computer Science",
                            "program": "Software Engineering",
                            "status": "Graduated",
                        },
                        "studentScore": {
                            "grade": "A",
                            "gpa": 4.0,
                            "descriptor": "Excellent",
                        },
                    }
                }
            },
        }
        if profile_id == "myUniCredential"
        else {
            "profileId": {profile_id},
            "authMethod": "PRE_AUTHORIZED",
            "expiresInSeconds": -1,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "waltid-pytest/1.0"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            response_body = resp.read().decode("utf-8")
            data = json.loads(response_body)

            print(f"  HTTP Status: {status}")
            print(f"  Response Body: {json.dumps(data, indent=2)}")

            assert status == 201, f"Expected HTTP 201, got {status}"

            # Assert offer exists
            offer_id = data.get("offerId")
            assert offer_id is not None, "Response JSON missing 'offerId' field!"
            offer_url = data.get("credentialOffer")
            assert offer_url is not None, (
                "Response JSON missing 'credentialOffer' field!"
            )
            print(f"  [SUCCESS] Created Offer: {offer_id}")
            return str(offer_url)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"  [-] HTTP Error {e.code}: {error_body}")
        sys.exit(1)


def test_receive_offer(wallet_id, offer_url):
    """POST /wallet/{wallet_id}/credentials/receive to receive a created offer."""
    url = f"http://{HOST}:{WALLET_PORT}/wallet/{wallet_id}/credentials/receive"
    print(f"\n[TEST 6] POST {url} (Receive Created Offer)...")

    payload = json.dumps({"offerUrl": offer_url}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "waltid-pytest/1.0"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            response_body = resp.read().decode("utf-8")
            data = json.loads(response_body)

            print(f"  HTTP Status: {status}")
            print(f"  Response Body: {json.dumps(data, indent=2)}")

            assert status == 200, f"Expected HTTP 200, got {status}"

            # Assert 'credentialIds' exists
            credential_ids = data.get("credentialIds")
            assert credential_ids is not None, (
                "Response JSON missing 'credentialIds' field!"
            )

            print(f"  [SUCCESS] Recived Offer: {credential_ids}")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"  [-] HTTP Error {e.code}: {error_body}")
        sys.exit(1)


if __name__ == "__main__":
    print("==================================================")
    print("   walt.id REST API Test Suite (Python)           ")
    print("==================================================")

    # 1. Container Readiness Checks
    wait_for_service(f"http://{HOST}:{WALLET_PORT}", "Wallet API 2")
    wait_for_service(f"http://{HOST}:{ISSUER_PORT}", "Issuer API 2")
    wait_for_service(f"http://{HOST}:{VERIFIER_PORT}", "Verifier API 2")

    # 2. Profile
    profile_id = "myUniCredential"

    # 3. REST API Functional Tests
    wallet_id = test_create_wallet()
    test_create_key(wallet_id)
    test_create_did(wallet_id)
    test_issuer_profile(profile_id)
    offer_url = test_issuer_create_offers(profile_id)
    test_receive_offer(wallet_id, offer_url)

    print("\n==================================================")
    print("   ALL REST API TESTS PASSED SUCCESSFULLY!        ")
    print("==================================================")
