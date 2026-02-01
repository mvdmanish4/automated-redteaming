# Dashboard Backend API

Backend API for the Red Team Demonstration Dashboard.

## Overview

This Flask API provides endpoints to interact with the exploit tools and retrieve information about vulnerabilities in the vulnerable e-commerce application.

## Endpoints

### 1. Health Check
```
GET /health
```
Returns API health status.

### 2. Exploit Test
```
GET /api/exploit/test
```
Executes exploit commands with different asset names and returns request/response data for each test scenario.

**Response includes:**
- Request details (URL, payload, command)
- Response data (status code, headers, output)
- Timing information
- Exploit success status

### 3. List CVEs
```
GET /api/cves
```
Returns a list of CVEs found in the application, including:
- CVE-2024-COMMAND-INJECTION (CRITICAL) - Main vulnerability
- 4 additional CVEs with lower severity (MEDIUM/LOW)

**Response includes:**
- CVE ID, CWE ID, title
- Severity and CVSS score
- Description and impact
- Affected endpoints
- References

### 4. Get Exploit Script
```
GET /api/exploit/script?type=exploit
GET /api/exploit/script?type=read_file
```
Returns the content of the exploit script.

**Parameters:**
- `type`: `exploit` (default) or `read_file`

### 5. Execute Exploit
```
POST /api/exploit/execute
```
Executes exploit commands via HTTP requests and returns request/response data (similar to curl output). Does NOT execute the Python scripts, but makes HTTP requests directly to the vulnerable endpoint.

**Request Body:**
```json
{
  "type": "exploit",
  "target_url": "https://vulnerable-ecommerce-6pgqjb4bma-uc.a.run.app",
  "asset_name": "api-server"
}
```

Or for read_file type:
```json
{
  "type": "read_file",
  "target_url": "https://vulnerable-ecommerce-6pgqjb4bma-uc.a.run.app",
  "file_path": "productdata.txt",
  "asset_name": "api-server"
}
```

**Response includes:**
- Script content (for reference)
- Request details (URL, payload, command, method)
- Response data (status code, headers, output, data)
- Timing information
- Exploit success status (detected from output)

### 6. Read File Exploit
```
POST /api/exploit/read-file
```
Executes read_file exploit via HTTP request and returns request/response data. Makes an HTTP request directly to exfiltrate a specific file.

**Request Body:**
```json
{
  "target_url": "https://vulnerable-ecommerce-6pgqjb4bma-uc.a.run.app",
  "file_path": "productdata.txt",
  "asset_name": "api-server"
}
```

**Response includes:**
- Script content (for reference)
- Request details (URL, payload, command)
- Response data (status code, headers, output with file contents)
- Timing information
- Exploit success status

### 7. Send Exploit Report Email
```
POST /api/email/send
```
Sends an email using Resend API with exploit details, results, and a call to action to generate PR.

**Request Body:**
```json
{
  "to": "security-team@example.com",
  "exploit_results": {
    "exploit_success": true,
    "request": {
      "command": "cat productdata.txt",
      "asset_name": "api-server"
    },
    "response": {
      "status_code": 200,
      "output": "...",
      "output_length": 5020
    }
  },
  "target_url": "https://vulnerable-ecommerce-6pgqjb4bma-uc.a.run.app"
}
```

**Response includes:**
- Email ID from Resend
- Recipient email
- Subject line
- Success status

**Environment Variables Required:**
- `RESEND_API_KEY`: Your Resend API key
- `RESEND_FROM_EMAIL`: Sender email address (default: "Red Team Demo <onboarding@resend.dev>")

### 8. Generate Pull Request
```
GET /api/generate-pr
```
Generates a pull request with security fixes (returns success message).

**Query Parameters (optional):**
- `title`: PR title (default: "Security Fix: Command Injection Vulnerability")
- `description`: PR description (default: auto-generated)

**Example:**
```
GET /api/generate-pr?title=Custom%20Title&description=Custom%20Description
```

**Response includes:**
- PR status and number
- PR URL (mock)
- Branch name
- List of changes
- Description

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set environment variables:
- `TARGET_URL`: Target vulnerable application URL (default: GCP Cloud Run URL)
- `PORT`: API server port (default: 5001)
- `RESEND_API_KEY`: Resend API key for sending emails (required for `/api/email/send`)
- `RESEND_FROM_EMAIL`: Sender email address for Resend (default: "Red Team Demo <onboarding@resend.dev>")

## Running

```bash
python app.py
```

Or with environment variables:
```bash
TARGET_URL=https://vulnerable-ecommerce-6pgqjb4bma-uc.a.run.app PORT=5001 python app.py
```

## Example Usage

### Test exploit commands:
```bash
curl https://6abb35913592.ngrok-free.app/api/exploit/test
```

### Get list of CVEs:
```bash
curl https://6abb35913592.ngrok-free.app/api/cves
```

### Get exploit script:
```bash
curl https://6abb35913592.ngrok-free.app/api/exploit/script?type=exploit
```

### Execute exploit (returns HTTP response data):
```bash
curl -X POST https://6abb35913592.ngrok-free.app/api/exploit/execute \
  -H "Content-Type: application/json" \
  -d '{
    "type": "read_file",
    "target_url": "https://vulnerable-ecommerce-6pgqjb4bma-uc.a.run.app",
    "file_path": "productdata.txt",
    "asset_name": "api-server"
  }'
```

### Read file exploit:
```bash
curl -X POST https://6abb35913592.ngrok-free.app/api/exploit/read-file \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://vulnerable-ecommerce-6pgqjb4bma-uc.a.run.app",
    "file_path": "productdata.txt",
    "asset_name": "monitoring.vulnmart.internal"
  }'
```

### Send exploit report email:
```bash
curl -X POST https://6abb35913592.ngrok-free.app/api/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "security-team@example.com",
    "exploit_results": {
      "exploit_success": true,
      "request": {
        "command": "cat productdata.txt",
        "asset_name": "api-server"
      },
      "response": {
        "status_code": 200,
        "output": "VULNMART CONFIDENTIAL PRODUCT DATA...",
        "output_length": 5020
      }
    }
  }'
```

### Generate pull request:
```bash
curl https://6abb35913592.ngrok-free.app/api/generate-pr
```

Or with optional parameters:
```bash
curl "https://6abb35913592.ngrok-free.app/api/generate-pr?title=Security%20Fix&description=Custom%20description"
```

## Notes

- The API disables SSL verification for testing purposes
- Execute endpoints make HTTP requests directly (do not execute Python scripts)
- Execute endpoints return request/response data similar to curl output
- Request timeout is 30 seconds for HTTP requests
- All endpoints return JSON responses
- CORS is enabled for frontend access
- Default port is 5001 (changed from 5000 to avoid conflicts with macOS ControlCenter)
- Email sending requires Resend API key (get one at https://resend.com)
- Generate PR endpoint is a mock implementation (returns success message with mock PR details)