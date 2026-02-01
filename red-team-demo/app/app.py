#!/usr/bin/env python3
"""
Vulnerable E-commerce Application
=================================
⚠️  WARNING: This application contains INTENTIONAL SECURITY VULNERABILITIES ⚠️
⚠️  FOR EDUCATIONAL AND AUTHORIZED TESTING PURPOSES ONLY ⚠️

This Flask application demonstrates a command injection vulnerability
similar to CVE-2021-41773. It is designed for red team training and
security awareness demonstrations.

NEVER deploy this application in a production environment.
NEVER use against systems without explicit authorization.

Author: Red Team Demo Project
License: MIT (Educational Use Only)
"""

import subprocess
import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Application metadata
APP_NAME = "VulnMart E-commerce API"
APP_VERSION = "1.0.0"

# HTML template for the home page
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_name }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e6e6e6;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        h1 {
            color: #e94560;
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .version {
            color: #888;
            font-size: 0.9rem;
        }
        .warning-banner {
            background: linear-gradient(90deg, #ff6b6b, #ee5a5a);
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(238, 90, 90, 0.3);
        }
        .endpoints {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        h2 {
            color: #e94560;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }
        .endpoint {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #e94560;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .endpoint:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 20px rgba(233, 69, 96, 0.2);
        }
        .method {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 0.8rem;
            margin-right: 10px;
        }
        .get { background: #4CAF50; color: white; }
        .path {
            font-family: 'Courier New', monospace;
            color: #00d9ff;
            font-weight: bold;
        }
        .description {
            color: #aaa;
            margin-top: 10px;
            font-size: 0.9rem;
        }
        .vulnerable {
            border-left-color: #ff6b6b;
            background: rgba(255, 107, 107, 0.1);
        }
        .vuln-tag {
            background: #ff6b6b;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.7rem;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        footer {
            text-align: center;
            margin-top: 40px;
            color: #666;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛒 {{ app_name }}</h1>
            <p class="version">Version {{ version }}</p>
        </header>
        
        <div class="warning-banner">
            ⚠️ VULNERABLE APPLICATION - FOR AUTHORIZED TESTING ONLY ⚠️
        </div>
        
        <div class="endpoints">
            <h2>📡 API Endpoints</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/</span>
                <p class="description">Home page - API documentation</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/health</span>
                <p class="description">Health check endpoint for monitoring</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/products</span>
                <p class="description">List all available products</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/search?q=&lt;query&gt;</span>
                <p class="description">Search products by name or description</p>
            </div>
            
            <div class="endpoint vulnerable">
                <span class="method get">GET</span>
                <span class="path">/ping?host=&lt;hostname&gt;</span>
                <span class="vuln-tag">🔓 VULNERABLE</span>
                <p class="description">Network diagnostic utility - Ping a host to check connectivity</p>
            </div>
        </div>
        
        <footer>
            <p>🔴 Red Team Demonstration Project | Educational Use Only</p>
        </footer>
    </div>
</body>
</html>
"""

# Sample product data
PRODUCTS = [
    {
        "id": 1,
        "name": "Premium Wireless Headphones",
        "price": 299.99,
        "category": "Electronics",
        "description": "High-quality noise-canceling wireless headphones"
    },
    {
        "id": 2,
        "name": "Smart Watch Pro",
        "price": 449.99,
        "category": "Electronics",
        "description": "Advanced smartwatch with health monitoring"
    },
    {
        "id": 3,
        "name": "Organic Coffee Beans",
        "price": 24.99,
        "category": "Food",
        "description": "Premium single-origin organic coffee"
    },
    {
        "id": 4,
        "name": "Ergonomic Office Chair",
        "price": 599.99,
        "category": "Furniture",
        "description": "Adjustable ergonomic chair with lumbar support"
    },
    {
        "id": 5,
        "name": "4K Gaming Monitor",
        "price": 799.99,
        "category": "Electronics",
        "description": "32-inch 4K monitor with 144Hz refresh rate"
    }
]


@app.route('/')
def home():
    """Render the home page with API documentation."""
    return render_template_string(
        HOME_TEMPLATE,
        app_name=APP_NAME,
        version=APP_VERSION
    )


@app.route('/health')
def health():
    """Health check endpoint for monitoring and load balancers."""
    return jsonify({
        'status': 'healthy',
        'app': APP_NAME,
        'version': APP_VERSION,
        'environment': os.environ.get('ENVIRONMENT', 'development')
    })


@app.route('/products')
def get_products():
    """Return all products in the catalog."""
    return jsonify({
        'success': True,
        'count': len(PRODUCTS),
        'products': PRODUCTS
    })


@app.route('/search')
def search_products():
    """Search products by query string."""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({
            'success': False,
            'error': 'Missing search query. Use ?q=<search_term>'
        }), 400
    
    results = [
        p for p in PRODUCTS
        if query in p['name'].lower() or query in p['description'].lower()
    ]
    
    return jsonify({
        'success': True,
        'query': query,
        'count': len(results),
        'results': results
    })


@app.route('/ping')
def ping():
    """
    Network diagnostic utility - Ping a specified host.
    
    ⚠️ VULNERABILITY: Command Injection (CWE-78)
    ============================================
    This endpoint is INTENTIONALLY VULNERABLE to command injection attacks.
    The 'host' parameter is passed directly to a shell command without
    any input validation or sanitization.
    
    Attack vectors:
    - Command chaining: ; && ||
    - Command substitution: $() ``
    - Piping: |
    
    Similar to: CVE-2021-41773 (Apache Path Traversal/RCE)
    
    Example exploits:
    - /ping?host=localhost;id
    - /ping?host=localhost;cat /etc/passwd
    - /ping?host=localhost|whoami
    """
    host = request.args.get('host', 'localhost')
    
    try:
        # ⚠️ VULNERABLE CODE - DO NOT USE IN PRODUCTION ⚠️
        # The 'host' parameter is directly interpolated into the shell command
        # without any sanitization, allowing arbitrary command execution.
        command = f'ping -c 1 {host}'
        
        # Using shell=True with unsanitized input is the vulnerability
        result = subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=30
        )
        
        return jsonify({
            'success': True,
            'host': host,
            'command': command,
            'output': result.decode('utf-8', errors='replace')
        })
        
    except subprocess.CalledProcessError as e:
        # Even errors can leak command output
        return jsonify({
            'success': False,
            'host': host,
            'error': 'Command failed',
            'output': e.output.decode('utf-8', errors='replace') if e.output else str(e)
        }), 500
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'host': host,
            'error': 'Command timed out after 30 seconds'
        }), 504
        
    except Exception as e:
        return jsonify({
            'success': False,
            'host': host,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': ['/', '/health', '/products', '/search', '/ping']
    }), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Get port from environment variable (Cloud Run sets this)
    port = int(os.environ.get('PORT', 8080))
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   ⚠️  VULNERABLE APPLICATION - EDUCATIONAL USE ONLY ⚠️        ║
    ║                                                              ║
    ║   This application contains INTENTIONAL security flaws.      ║
    ║   NEVER deploy in production or use without authorization.   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Starting {APP_NAME} v{APP_VERSION}
    Server running on http://0.0.0.0:{port}
    
    Endpoints:
    - GET /         - Home page
    - GET /health   - Health check
    - GET /products - List products
    - GET /search   - Search products
    - GET /ping     - Ping utility (VULNERABLE)
    """)
    
    app.run(host='0.0.0.0', port=port, debug=False)
