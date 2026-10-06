# Synixon Breach Investigation - Comprehensive Write-up

## Overview

This document details the network forensic analysis of the `synixon_breach_capture.pcapng` file. The objective was to track an attacker's steps, identify exploited vulnerabilities, uncover hidden web services, and extract flags purely through packet analysis using Wireshark.

## Challenge 2: Supervisor Email Identification

**Objective:** Find the email address the attacker or user interacted with over a chat session.
**Methodology:**

1. Opened the `synixon_breach_capture.pcapng` in Wireshark.
2. Located **WebSocket** traffic, which is commonly used for live chat applications.
3. Right-clicked a `WebSocket Text` packet and selected **Follow > TCP Stream** (or HTTP Stream).
4. Read through the plaintext chat logs looking for discussions regarding password resets or supervisor accounts.
5. Extracted the target email address directly from the conversation text.

## Challenge 3: Vulnerable Debug Page (LFI Identification)

**Objective:** Identify the vulnerable developer debug file used to execute a Local File Inclusion (LFI) attack.
**Methodology:**

1. Applied a Wireshark display filter to isolate web requests: `http.request.method == "GET"`
2. Used the string search function (**Ctrl+F**, set to *Packet Details* and *String*) to look for common directory traversal payloads like `../` or `passwd`.
3. Identified an HTTP GET request where the URL parameters attempted to access sensitive files (e.g., `?file=../../../../etc/passwd`).
4. Extracted the PHP file name immediately preceding the payload (e.g., `debug-test.php`).
   *(Note: We later observed the successful payload response containing `/bin/bash` in the `/etc/passwd` file output).*

## Challenge 6 & 7: Hidden Web Service and Admin Login

**Objective:** Discover a hidden web service running on a high-number, 5-digit port and locate the hidden admin login page.
**Methodology:**

1. To find the non-standard web server port, we analyzed traffic using display filters. While filtering out known web traffic later in the investigation, we spotted standard HTTP `200 OK` responses originating from a 5-digit port.
2. **Challenge 6 Answer:** The hidden web service was running on port **17645**.
3. With the port identified, we inspected the HTTP GET requests being directed to this specific port.
4. **Challenge 7 Answer:** By reviewing the `Request URI` in the HTTP headers sent to port 17645, we identified the hidden administrative file matching the required pattern (e.g., `admin_login_XXXXNNXN.php`).

## Challenge 8: Legacy Feedback Service

**Objective:** Identify the 4-digit port running the legacy feedback service.
**Methodology:**

1. Examined the general TCP/HTTP traffic captured in the pcap.
2. Looked closely at the Transmission Control Protocol (TCP) headers in the packet details pane.
3. Identified web requests pointing to an internal legacy application.
4. **Answer:** The legacy service was running on port **5000**.

## Challenge 9: Locating the Attacker's Reverse Shell

**Objective:** Find the attacker's IP address and the specific listening port used for the reverse shell connection.
**Methodology:**

1. We knew the victim IP was `10.10.1.111` and the suspected attacker IP was `10.10.1.2`.
2. To isolate the reverse shell from the noisy web traffic, we applied a strict Wireshark exclusion filter to remove all known web services (ports 80, 5000, and 17645):
   ```text
   ip.src == 10.10.1.111 and ip.dst == 10.10.1.2 and tcp.srcport != 80 and tcp.srcport != 5000 and tcp.srcport != 17645
   ```
3. This filter perfectly isolated the backdoor connection.
4. Checking the TCP headers of the remaining packets revealed the attacker's destination port.
5. **Answer:** The attacker IP and listening port was `10.10.1.2:8998`.

## Challenge 10: Extracting the Reverse Shell Flag

**Objective:** Capture the final flag from the attacker's interactive shell session.
**Methodology:**

1. Using the isolated traffic from Challenge 9 (the connection on port 8998), we right-clicked the packet and selected **Follow > TCP Stream**.
2. This revealed the plaintext command-line session between the attacker and the compromised server.
3. We observed the attacker running the following enumeration and exfiltration commands:
   ```bash
   /usr/bin/find / -name flag.txt 2>/dev/null
   /home/flag.txt
   /usr/bin/cat /home/flag.txt
   ```
4. **Answer:** The system outputted the final flag in the stream: `flag{A1EL2L8P}`.

*End of Report*