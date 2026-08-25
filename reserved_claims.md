# Reserved Claims and Configuration Keys Reference for walt.id

This reference document outlines all reserved claims, structural properties, and configuration keys across **SD-JWT VC (`dc+sd-jwt`)**, **W3C Verifiable Credentials (`jwt_vc_json`)**, **OpenID4VCI**, and **walt.id Issuer 2 profiles**.

Using any of these reserved names for arbitrary user domain fields—or using an incorrect data type (such as passing a string literal where a `JsonObject` is expected)—will lead to runtime deserialization or issuance failures (e.g. `Element class kotlinx.serialization.json.JsonLiteral is not a JsonObject`).

---

## 1. SD-JWT VC & OpenID4VCI Reserved Claims (`dc+sd-jwt`)

In SD-JWT VC credentials, custom claims are placed at the root level of `credentialData`. The claims below are reserved by the IETF SD-JWT VC specification, OpenID4VCI protocol, and walt.id's engine:

| Claim Name | Expected Type | Protocol / Specification | Description & Common Pitfalls |
| :--- | :--- | :--- | :--- |
| **`status`** | `JsonObject` | IETF SD-JWT VC / OAuth Status List | **Credential Revocation / Status List Info**. Expects an object containing status list metadata (e.g. `status_list`, `uri`, `idx`). **Do not use for domain status** like `"status": "Studying"` or `"status": "Active"`. Use `studentStatus`, `accountStatus`, etc. instead. |
| **`vct`** | `String` (URI / URN) | IETF SD-JWT VC | **Verifiable Credential Type**. The unique type identifier or schema URL for the SD-JWT credential. |
| **`cnf`** | `JsonObject` | RFC 7800 / SD-JWT VC | **Confirmation claim**. Holds the holder key binding proof (e.g. `{"jwk": { ... }}` or `{"x5t#S256": "..."}`). |
| **`_sd`** | `Array<String>` | IETF SD-JWT | **Selective Disclosure digests**. Auto-generated array containing salted hashes of selectively disclosed claims. |
| **`_sd_alg`** | `String` | IETF SD-JWT | **Hash algorithm identifier** for selective disclosure digests (default: `"sha-256"`). |
| **`iss`** / **`issuer`** | `String` (URI / DID) | RFC 7519 / SD-JWT VC | **Issuer identifier**. Represents the entity issuing the credential. |
| **`sub`** | `String` (DID / URI) | RFC 7519 / SD-JWT VC | **Subject identifier** (holder DID). |
| **`iat`** | `Long` / `Integer` | RFC 7519 | **Issued At timestamp** (Epoch seconds, e.g. `"<timestamp-seconds>"`). |
| **`nbf`** | `Long` / `Integer` | RFC 7519 | **Not Before timestamp** (Epoch seconds). |
| **`exp`** | `Long` / `Integer` | RFC 7519 | **Expiration timestamp** (Epoch seconds). |
| **`jti`** | `String` | RFC 7519 | **JWT ID** (unique identifier for the token instance, e.g. `"<uuid>"`). |
| **`aud`** | `String` or `Array<String>` | RFC 7519 | **Audience** for which the credential or proof is intended. |

---

## 2. W3C Verifiable Credentials Reserved Claims (`jwt_vc_json`)

In W3C JSON-LD / JWT Verifiable Credentials, custom domain claims are placed inside the `credentialSubject` object. The outer credential envelope reserves the following fields:

| Field Name | Expected Type | Specification | Description |
| :--- | :--- | :--- | :--- |
| **`credentialSubject`** | `JsonObject` | W3C VC Data Model | Payload container holding all subject/user domain claims. |
| **`credentialStatus`** | `JsonObject` | W3C VC Data Model | W3C Revocation Status specification object (includes `id`, `type`, etc.). |
| **`@context`** | `Array<String>` | W3C VC Data Model | JSON-LD schema context definitions (e.g. `["https://www.w3.org/2018/credentials/v1"]`). |
| **`type`** | `Array<String>` | W3C VC Data Model | Credential types list (e.g. `["VerifiableCredential", "MyUniCredential"]`). |
| **`id`** | `String` (URI) | W3C VC Data Model | Unique credential identifier URI (e.g. `urn:uuid:...`). |
| **`issuanceDate`** / **`validFrom`** | `String` (ISO 8601 UTC) | W3C VC Data Model (v1 / v2) | Issuance timestamp. |
| **`expirationDate`** / **`validUntil`** | `String` (ISO 8601 UTC) | W3C VC Data Model (v1 / v2) | Expiration timestamp. |
| **`credentialSchema`** | `JsonObject` or `Array` | W3C VC Data Model | Schema validator references. |
| **`evidence`** | `Array<JsonObject>` | W3C VC Data Model | Evidence records supporting issuance. |
| **`termsOfUse`** | `Array<JsonObject>` | W3C VC Data Model | Usage terms and restrictions. |
| **`refreshService`** | `JsonObject` | W3C VC Data Model | Endpoint metadata for refreshing the credential. |

---

## 3. walt.id Profile Config Reserved Keys (`issuer2-profiles.conf`)

Inside each profile block in `issuer2-profiles.conf`, the top-level keys reserved by walt.id are:

| Key Name | Type | Purpose |
| :--- | :--- | :--- |
| **`name`** | `String` | Human-readable name of the profile. |
| **`credentialConfigurationId`** | `String` | Identifier matching an entry in `credential-issuer-metadata.conf`. |
| **`issuerKey`** | `Object` / `${...}` | Reference or inline definition of the issuer private signing key. |
| **`issuerDid`** | `String` / `${...}` | Reference or inline definition of the issuer DID. |
| **`x5Chain`** | `Array<String>` | X.509 certificate chain (PEM / DER) for mdoc / SD-JWT signatures. |
| **`credentialData`** | `JsonObject` | Template payload holding the claims to be issued. |
| **`mapping`** | `JsonObject` | Dynamic template replacement rules (e.g. `<uuid>`, `<timestamp-seconds>`, `<issuerDid>`, `<subjectDid>`). |
| **`selectiveDisclosure`** | `JsonObject` | SD-JWT configuration block containing `fields`, `decoyMode`, and `decoys`. |
| **`idTokenClaimsMapping`** | `JsonObject` | JSONPath mapping for OpenID4VP / OIDC claim extraction. |
| **`mDocNameSpacesDataMappingConfig`** | `JsonObject` | Data-type converter mappings for ISO 18013-5 mdoc namespaces. |
| **`credentialStatus`** | `JsonObject` | Status list binding configuration for issuer status tracking. |

---

## 4. Best Practices for Domain Models

1. **Avoid Generic Single-Word Claim Names at the Root of SD-JWTs**:
   - Instead of `status`, use domain-specific names like `studentStatus`, `enrollmentStatus`, `membershipStatus`, or `accountStatus`.
   - Instead of `id`, use `studentId`, `employeeId`, or `citizenId` to avoid conflicts with `jti`/`id`/`sub`.
   - Instead of `type`, use `credentialType`, `studentType`, or `degreeType`.
2. **Match Field Names Across Layers**:
   Ensure that domain entity properties (e.g. in C# / Java), configuration templates (`issuer2-profiles.conf`), and test queries (DCQL queries in `test_waltid_api.py`) use identical claim names.
3. **Verify Nested Profile Syntax in HOCON**:
   Always verify that each profile in `issuer2-profiles.conf` is keyed by its identifier:
   ```hocon
   profiles {
     myProfileId {
       name = "My Profile"
       credentialConfigurationId = "my_profile_config"
       # ...
     }
   }
   ```
