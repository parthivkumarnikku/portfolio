# TryHeartMe

> Challange Description:
> *The TryHeartMe shop is open for business. Can you find a way to purchase the hidden “Valenflag” item?*


Title: Love at first breach - TryHeartMe
Date: 2026-02-16
Author: scap3sh4rk
Tags: [web, jwt, informative]

## Challenge Metadata

- **Room Name:** TryHeartMe
- **Platform:** TryHackMe
- **URL:** [Link to the challenge](https://tryhackme.com/room/lafb2026e5)
- **Difficulty:** Easy
- **Category:** Web
- **Points:** 100

---

## Introduction

There is the web app, a shop app basically as the landing page. This description says that there is a hidden item in the store that can be bought, 
Initially i tried looking up the `styles.css` and `.js` file to see something interesting found - meaning, thought its something to do with `UI`. The js has comething called `.toast` which is basically to hide stuff but in this case, its just hiding the acknoledgement messages.

## 1. Reconnaissance

I started scanning the directories brute-force using ffuf and found that there is a directory called admin.
```bash
ffuf -u http://$TARGET:5000/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt
```



After trying to open it, found that its forbidden and this is something based on authorization and looked for details are are responsible for authorization across the website.

<!--GIT STYLE PLACEHOLDER FOR FILE - FORBIDDEN-->

## Conclusion

Summarize the key takeaways from this write-up. What did you learn? What are the main remediation steps to prevent this kind of vulnerability?

> "A cool quote or a final thought." — Author

---

*This is a template for a CTF write-up. Replace the placeholder text with your own content.*
