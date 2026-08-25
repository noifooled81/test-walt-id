"""
walt.id REST API Test Suite (Python)
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from http.client import HTTPResponse
from typing import Any, cast

# Environment variable ports matching walt.id setup
ISSUER_PORT = os.getenv("ISSUER_API2_PORT", "7005")
VERIFIER_PORT = os.getenv("VERIFIER_API2_PORT", "7004")
WALLET_PORT = os.getenv("WALLET_API2_PORT", "7006")
HOST = os.getenv("HOST", "localhost")

MAX_RETRIES = 10
RETRY_INTERVAL = 2


def wait_for_service(url: str, service_name: str) -> bool:
    """Polls a service URL until it responds or timeout limit is reached."""
    print(f"[WAIT] Checking {service_name} at {url}...")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "waltid-pytest/1.0"}
            )
            with urllib.request.urlopen(req, timeout=3) as _resp:  # pyright: ignore[reportAny]
                resp = cast(HTTPResponse, _resp)
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
        with urllib.request.urlopen(req) as _resp:  # pyright: ignore[reportAny]
            resp = cast(HTTPResponse, _resp)
            status = resp.status
            response_body = resp.read().decode("utf-8")
            data = cast(dict[str, Any], json.loads(response_body))  # pyright: ignore[reportExplicitAny]

            print(f"  HTTP Status: {status}")
            print(f"  Response Body: {json.dumps(data, indent=2)}")

            assert status == 201, f"Expected HTTP 201, got {status}"

            wallet_id = cast(str, data.get("walletId") or data.get("id"))
            assert wallet_id is not None, "Response JSON missing 'walletId' field!"

            print(f"  [SUCCESS] Created Wallet ID: {wallet_id}")
            return wallet_id

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"  [-] HTTP Error {e.code}: {error_body}")
        sys.exit(1)


def test_create_key(wallet_id: str) -> None:
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
        with urllib.request.urlopen(req) as _resp:  # pyright: ignore[reportAny]
            resp = cast(HTTPResponse, _resp)
            status = resp.status
            response_body = resp.read().decode("utf-8")
            data = cast(dict[str, Any], json.loads(response_body))  # pyright: ignore[reportExplicitAny]

            print(f"  HTTP Status: {status}")
            print(f"  Response Body: {json.dumps(data, indent=2)}")

            assert status == 201, f"Expected HTTP 201, got {status}"

            key_id = cast(str, data.get("keyId") or data.get("id"))
            assert key_id is not None, "Response JSON missing 'keyId' field!"

            print(f"  [SUCCESS] Created Wallet Key ID: {key_id}")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"  [-] HTTP Error {e.code}: {error_body}")
        sys.exit(1)


def test_create_did(wallet_id: str) -> None:
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
        with urllib.request.urlopen(req) as _resp:  # pyright: ignore[reportAny]
            resp = cast(HTTPResponse, _resp)
            status = resp.status
            response_body = resp.read().decode("utf-8")
            data = cast(dict[str, Any], json.loads(response_body))  # pyright: ignore[reportExplicitAny]

            print(f"  HTTP Status: {status}")
            print(f"  Response Body: {json.dumps(data, indent=2)}")

            assert status == 201, f"Expected HTTP 201, got {status}"

            did = cast(str, data.get("did") or data.get("id"))
            assert did is not None, "Response JSON missing 'did' field!"

            print(f"  [SUCCESS] Created Wallet DID: {did}")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"  [-] HTTP Error {e.code}: {error_body}")
        sys.exit(1)


def test_issuer_profile() -> None:
    """GET /issuer2/profiles/myUniCredentialSD to verify generated entity profile."""
    url = f"http://{HOST}:{ISSUER_PORT}/issuer2/profiles/myUniCredentialSD"
    print(f"\n[TEST 4] GET {url} (Verify Custom Profile)...")
    try:
        with urllib.request.urlopen(url) as _resp:  # pyright: ignore[reportAny]
            resp = cast(HTTPResponse, _resp)
            status = resp.status
            data = cast(dict[str, Any], json.loads(resp.read().decode("utf-8")))  # pyright: ignore[reportExplicitAny]
            assert status == 200, f"Expected HTTP 200, got {status}"
            profile_name = cast(str, data.get("name", "myUniCredentialSD"))
            print(f"  [SUCCESS] Loaded Profile: {profile_name}")
    except urllib.error.HTTPError as e:
        print(f"  [-] HTTP Error {e.code}: {e.read().decode('utf-8')}")


def test_issuer_create_offers() -> tuple[str, dict[str, Any]]:  # pyright: ignore[reportExplicitAny]
    """POST /issuer2/credential-offers to create a new offer."""
    url = f"http://{HOST}:{ISSUER_PORT}/issuer2/credential-offers"
    print(f"\n[TEST 5] POST {url} (Create New Offer)...")

    payload_data: dict[str, Any] = (  # pyright: ignore[reportExplicitAny]
        {
            "profileId": "myUniCredentialSD",
            "authMethod": "PRE_AUTHORIZED",
            "runtimeOverrides": {
                "credentialData": {
                    "firstName": "Jane",
                    "lastName": "Kim",
                    "birthdate": "1999-01-01T00:00:00Z",
                    "gender": "Female",
                    "intake": 2019,
                    "school": "School of Computer Science",
                    "program": "Software Engineering",
                    "studentStatus": "Graduated",
                    "grade": "A",
                    "gpa": 4.0,
                    "descriptor": "Excellent",
                }
            },
        }
    )

    payload = json.dumps(payload_data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "waltid-pytest/1.0"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as _resp:  # pyright: ignore[reportAny]
            resp = cast(HTTPResponse, _resp)
            status = resp.status
            response_body = resp.read().decode("utf-8")
            data = cast(dict[str, Any], json.loads(response_body))  # pyright: ignore[reportExplicitAny]

            print(f"  HTTP Status: {status}")
            print(f"  Response Body: {json.dumps(data, indent=2)}")

            assert status == 201, f"Expected HTTP 201, got {status}"

            offer_id = cast(str, data.get("offerId"))
            assert offer_id is not None, "Response JSON missing 'offerId' field!"
            offer_url = cast(str, data.get("credentialOffer"))
            assert offer_url is not None, (
                "Response JSON missing 'credentialOffer' field!"
            )
            print(f"  [SUCCESS] Created Offer: {offer_id}")
            return offer_url, payload_data

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"  [-] HTTP Error {e.code}: {error_body}")
        sys.exit(1)


def test_receive_offer(wallet_id: str, offer_url: str) -> list[str]:
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
        with urllib.request.urlopen(req) as _resp:  # pyright: ignore[reportAny]
            resp = cast(HTTPResponse, _resp)
            status = resp.status
            response_body = resp.read().decode("utf-8")
            data = cast(dict[str, Any], json.loads(response_body))  # pyright: ignore[reportExplicitAny]

            print(f"  HTTP Status: {status}")
            print(f"  Response Body: {json.dumps(data, indent=2)}")

            assert status == 200, f"Expected HTTP 200, got {status}"

            credential_ids = cast(list[str], data.get("credentialIds"))
            assert credential_ids is not None, (
                "Response JSON missing 'credentialIds' field!"
            )

            print(f"  [SUCCESS] Received Offer: {credential_ids}")
            return credential_ids

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"  [-] HTTP Error {e.code}: {error_body}")
        sys.exit(1)


def test_raw_offer_correctness(
    wallet_id: str,
    credential_id: str,
    payload_data: dict[str, Any],  # pyright: ignore[reportExplicitAny]
    i: int,
) -> None:
    """GET /wallet/{wallet_id}/credentials/{credential_id} to check correctness of created offer."""
    url = f"http://{HOST}:{WALLET_PORT}/wallet/{wallet_id}/credentials/{credential_id}"
    print(f"\n[TEST 7.{i}] GET {url} (Verify Created Offer {credential_id})...")

    try:
        with urllib.request.urlopen(url) as _resp:  # pyright: ignore[reportAny]
            resp = cast(HTTPResponse, _resp)
            status = resp.status
            data = cast(dict[str, Any], json.loads(resp.read().decode("utf-8")))  # pyright: ignore[reportExplicitAny]
            assert status == 200, f"Expected HTTP 200, got {status}"

            overriden = payload_data.get("runtimeOverrides")
            if overriden is None:
                print(f"  [SKIP] Offer: {credential_id}")
                return

            cred_data = cast(
                dict[str, Any],  # pyright: ignore[reportExplicitAny]
                payload_data["runtimeOverrides"]["credentialData"],
            )

            # In dc+sd-jwt, the type/vct identifier is typically 'vct' or parsed into data
            vct = data.get("vct") or data.get("type")
            if vct == "MyUniCredential" or "MyUniCredential" in str(vct):
                first_name = cast(str, data.get("firstName"))
                assert first_name == cred_data["firstName"], (
                    f"Expect Jane, got {first_name}"
                )

                last_name = cast(str, data.get("lastName"))
                assert last_name == cred_data["lastName"], (
                    f"Expect Kim, got {last_name}"
                )

                gender = cast(str, data.get("gender"))
                assert gender == cred_data["gender"], f"Expect Female, got {gender}"

                intake = cast(int, data.get("intake"))
                assert intake == cred_data["intake"], f"Expect 2019, got {intake}"

                cred_status = cast(str, data.get("studentStatus"))
                assert cred_status == cred_data["studentStatus"], (
                    f"Expect Graduated, got {cred_status}"
                )

            print(f"  [SUCCESS] Verified Offer: {credential_id}")

    except urllib.error.HTTPError as e:
        print(f"  [-] HTTP Error {e.code}: {e.read().decode('utf-8')}")

'''
    Verification request can be made by other instances (doesn't need to be the same network as issuer/holder) 
    and may not be awared of the credential structure. 
'''
def test_request_verification() -> tuple[str, str]:
    """POST /verification-session/create to create a verification request."""
    url = f"http://{HOST}:{VERIFIER_PORT}/verification-session/create"
    print(f"\n[TEST 8] POST {url} (Create Verification Request)...")

    payload = json.dumps(
        {
            "flow_type": "cross_device",
            "core_flow": {
                "dcql_query": {
                    "credentials": [
                        {
                            "id": "myUniCredential",
                            "format": "dc+sd-jwt",
                            "meta": {
                                "vct_values": [
                                    "http://host.docker.internal:7005/openid4vci/my_uni_credential_sd"
                                ]
                            },
                            "claims": [
                                {"path": ["firstName"]},
                                {"path": ["lastName"]},
                                {"path": ["birthdate"]},
                                {"path": ["gender"]},
                                {"path": ["studentStatus"]},
                                {"path": ["gpa"]}
                            ]
                        }
                    ]
                }
            }
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "waltid-pytest/1.0"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as _resp:  # pyright: ignore[reportAny]
            resp = cast(HTTPResponse, _resp)
            status = resp.status
            response_body = resp.read().decode("utf-8")
            data = cast(dict[str, Any], json.loads(response_body))  # pyright: ignore[reportExplicitAny]

            print(f"  HTTP Status: {status}")
            print(f"  Response Body: {json.dumps(data, indent=2)}")

            assert status == 200, f"Expected HTTP 200, got {status}"

            ses_id = cast(str, data.get("sessionId"))
            assert ses_id is not None, "Response JSON missing 'sessionId' field!"

            req_url = cast(str, data.get("bootstrapAuthorizationRequestUrl"))
            assert req_url is not None, (
                "Response JSON missing 'bootstrapAuthorizationRequestUrl' field!"
            )

            print(f"  [SUCCESS] Received Request URL: {req_url}")
            return ses_id, req_url

    except urllib.error.HTTPError as e:
        print(f"  [-] HTTP Error {e.code}: {e.read().decode('utf-8')}")
        sys.exit(1)


'''
    Present endpoint may give vague error msg when there is an error from wallet (e.g: claims not found).
    Prefer using isolated steps instead.
'''
def test_present_credential(wallet_id: str, req_url: str) -> None:
    """POST /wallet/{walletId}/credentials/present to create a presentation."""
    url = f"http://{HOST}:{WALLET_PORT}/wallet/{wallet_id}/credentials/present"
    print(f"\n[TEST 9] POST {url} (Create Presentation)...")

    payload = json.dumps({"requestUrl": req_url}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "waltid-pytest/1.0"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as _resp:  # pyright: ignore[reportAny]
            resp = cast(HTTPResponse, _resp)
            status = resp.status
            response_body = resp.read().decode("utf-8")
            data = cast(dict[str, Any], json.loads(response_body))  # pyright: ignore[reportExplicitAny]

            print(f"  HTTP Status: {status}")
            print(f"  Response Body: {json.dumps(data, indent=2)}")

            assert status == 200, f"Expected HTTP 200, got {status}"

            transmission_success = cast(bool, data.get("transmission_success"))
            assert transmission_success is True, (
                f"Expected true, got {transmission_success}"
            )

            verifier_response = cast(dict[str, Any], data.get("verifier_response", {}))  # pyright: ignore[reportExplicitAny]
            assert verifier_response is not None, (
                "Response JSON missing 'verifier_response' field!"
            )

            status_val = cast(str, verifier_response.get("status"))
            assert status_val == "received", f"Expected received, got {status_val}"

            print(f"  [SUCCESS] Presented Request URL: {req_url}")

    except urllib.error.HTTPError as e:
        print(f"  [-] HTTP Error {e.code}: {e.read().decode('utf-8')}")
        sys.exit(1)


def test_verifier_check_presentation(ses_id: str) -> None:
    """GET /verification-session/{sessionId}/info to check the status of the presentation."""
    url = f"http://{HOST}:{VERIFIER_PORT}/verification-session/{ses_id}/info"
    print(f"\n[TEST 10] GET {url} (Check presentation)...")

    req = urllib.request.Request(
        url,
        headers={"Content-Type": "application/json", "User-Agent": "waltid-pytest/1.0"},
        method="GET",
    )

    try:
        with urllib.request.urlopen(req) as _resp:  # pyright: ignore[reportAny]
            resp = cast(HTTPResponse, _resp)
            status = resp.status
            response_body = resp.read().decode("utf-8")
            data = cast(dict[str, Any], json.loads(response_body))  # pyright: ignore[reportExplicitAny]

            print(f"  HTTP Status: {status}")
            # print(f"  Response Body: {json.dumps(data, indent=2)}")

            assert status == 200, f"Expected HTTP 200, got {status}"

            presentation_status = cast(str, data.get("status"))
            assert presentation_status == "SUCCESSFUL", (
                f"Expected SUCCESSFUL, got {presentation_status}"
            )

            print(f"  [SUCCESS] Checked Presetation with session_id: {ses_id}")
    except urllib.error.HTTPError as e:
        print(f"  [-] HTTP Error {e.code}: {e.read().decode('utf-8')}")
        sys.exit(1)


if __name__ == "__main__":
    print("==================================================")
    print("   walt.id REST API Test Suite (Python)           ")
    print("==================================================")

    # 1. Container Readiness Checks
    _ = wait_for_service(f"http://{HOST}:{WALLET_PORT}", "Wallet API 2")
    _ = wait_for_service(f"http://{HOST}:{ISSUER_PORT}", "Issuer API 2")
    _ = wait_for_service(f"http://{HOST}:{VERIFIER_PORT}", "Verifier API 2")

    # 2. REST API Functional Tests
    wallet_id = test_create_wallet()
    test_create_key(wallet_id)
    test_create_did(wallet_id)
    test_issuer_profile()
    offer_url, payload_data = test_issuer_create_offers()
    credential_ids = test_receive_offer(wallet_id, offer_url)

    for i, cred_id in enumerate(credential_ids):
        test_raw_offer_correctness(wallet_id, cred_id, payload_data, i)

    ses_id, req_url = test_request_verification()
    test_present_credential(wallet_id, req_url)
    test_verifier_check_presentation(ses_id)

    print("\n==================================================")
    print("   ALL REST API TESTS PASSED SUCCESSFULLY!        ")
    print("==================================================")
