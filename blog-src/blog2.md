# Web Application Security: Understanding OWASP Top 10

*January 18, 2026 | Parthiv Kumar Nikku | Web Security | 12 min read*

## Introduction

Web applications are the backbone of modern digital services, making their security critically important. The OWASP (Open Web Application Security Project) Top 10 is the de facto standard for understanding the most critical web application security risks.

In this article, we'll explore each of the OWASP Top 10 vulnerabilities, how they can be exploited, and most importantly, how to prevent them.

## A01:2021 – Broken Access Control

Access control enforces policy such that users cannot act outside of their intended permissions. Failures typically lead to unauthorized information disclosure, modification, or destruction of data or performing business functions outside the user's limits.

### Common Vulnerabilities

*   Violation of the principle of least privilege
*   Bypassing access control checks by modifying the URL
*   Permitting viewing or editing someone else's account
*   Accessing API with missing access controls

### Prevention

*   Implement access control mechanisms once and re-use
*   Enforce record ownership vs. accepting user records
*   Disable directory listing
*   Log access control failures and alert administrators

## A02:2021 – Cryptographic Failures

The first thing is to determine the protection needs of data in transit and at rest. For example, passwords, credit card numbers, health records, personal information, and business secrets require extra protection.

### Common Vulnerabilities

*   Transmitting data in clear text
*   Using outdated or weak cryptographic algorithms
*   Default crypto keys or using weak keys
*   Not enforcing encryption (missing HTTPS)

```
# Example: Weak SSL/TLS configuration (BAD)
# Using deprecated protocols and weak ciphers
SSLProtocol all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
SSLCipherSuite HIGH:MEDIUM:!aNULL:!MD5

# Example: Strong configuration (GOOD)
SSLProtocol -all +TLSv1.2 +TLSv1.3
SSLCipherSuite TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
```

## A03:2021 – Injection

An application is vulnerable to attack when:

*   User-supplied data is not validated, filtered, or sanitized
*   Dynamic queries or non-parameterized calls are used
*   Hostile data is used within ORM search parameters
*   Hostile data is directly used or concatenated

### Prevention

*   Use parameterized queries (prepared statements)
*   Use LIMIT and other SQL controls to prevent mass disclosure
*   Use stored procedures
*   Validate, filter, and sanitize user input

```
// Vulnerable code (BAD)
String query = "SELECT * FROM users WHERE name = '" + userName + "'";

// Secure code (GOOD)
PreparedStatement pstmt = connection.prepareStatement(
    "SELECT * FROM users WHERE name = ?"
);
pstmt.setString(1, userName);
```

## A04:2021 – Insecure Design

Insecure design is a broad category representing different weaknesses, expressed as "missing or ineffective control design." There is a difference between insecure design and insecure implementation.

### Prevention

*   Use threat modeling for critical authentication
*   Use secure design pattern libraries
*   Implement segregation in the tenant (for multi-tenant)
*   Limit resource consumption per user

## A05:2021 – Security Misconfiguration

The application might be vulnerable if it is:

*   Missing security hardening across any part of the application stack
*   Using default credentials
*   Having unnecessary features enabled or installed
*   Error handling reveals stack traces

### Prevention

*   Repeatable hardening process
*   Minimal platform without unnecessary features
*   Review and update configurations per review
*   Segmented application architecture

## A06:2021 – Vulnerable and Outdated Components

You are likely vulnerable if:

*   You do not know all component versions
*   Software is unsupported or end-of-life
*   You do not scan for vulnerabilities regularly
*   You do not fix dependencies in a timely fashion

### Prevention

*   Remove unused dependencies
*   Continuously inventory component versions
*   Monitor for CVEs affecting your components
*   Only obtain components from official sources

## A07:2021 – Identification and Authentication Failures

Confirmation of the user's identity, authentication, and session management is critical to protect against authentication-related attacks.

### Common Vulnerabilities

*   Allowing automated attacks like credential stuffing
*   Permitting weak or default passwords
*   Having session IDs in the URL
*   Not rotating session IDs after login

```
// Example: Secure session management
// 1. Generate secure random session IDs
session_id = os.urandom(32).hex()

// 2. Set secure cookie attributes
response.set_cookie(
    'session_id',
    session_id,
    secure=True,        // HTTPS only
    httponly=True,     // No JavaScript access
    samesite='Strict'  // CSRF protection
)
```

## A08:2021 – Software and Data Integrity Failures

Software and data integrity failures relate to code and infrastructure that does not protect against integrity violations.

### Prevention

*   Use digital signatures for software/data
*   Verify NPM/Maven dependencies
*   Use a Software Composition Analysis (SCA) tool
*   Ensure CI/CD pipeline has proper access controls

## A09:2021 – Security Logging and Monitoring Failures

Insufficient logging, detection, monitoring, and active response occurs any time:

*   Logins, access control failures, and server-side input validation are not logged
*   Warning and errors generate no, inadequate, or unclear log messages
*   Application cannot detect, escalate, or alert for active attacks

### Prevention

*   Ensure logs contain sufficient context
*   Use centralized log management
*   Establish alerting thresholds and escalation
*   Implement incident response and recovery plans

## A10:2021 – Server-Side Request Forgery (SSRF)

SSRF flaws occur whenever a web application fetches remote resources without validating the user-supplied URL.

```
// Vulnerable code (BAD)
@app.route('/fetch_url')
def fetch_url():
    url = request.args.get('url')
    response = requests.get(url)  # No validation!
    return response.text

// Secure code (GOOD)
from urllib.parse import urlparse

@app.route('/fetch_url')
def fetch_url():
    url = request.args.get('url')
    parsed = urlparse(url)
    
    # Only allow http/https and specific domains
    if parsed.scheme not in ('http', 'https'):
        return "Invalid scheme", 400
    if parsed.hostname not in ('trusted.com',):
        return "Domain not allowed", 400
    
    response = requests.get(url)
    return response.text
```

## Conclusion

Understanding and addressing the OWASP Top 10 is essential for building secure web applications. Regular security assessments, code reviews, and staying updated with the latest security practices will help mitigate these vulnerabilities.

> "Applications security is not an afterthought, it's a feature."

Remember that security is an ongoing process. New vulnerabilities are discovered regularly, and your security practices should evolve accordingly.

---

*Author: Parthiv Kumar Nikku | CEHv13 | Security Researcher*
