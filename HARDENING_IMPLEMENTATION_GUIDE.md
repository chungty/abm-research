# ABM Dashboard Security Hardening Implementation Guide

## Priority 1: Critical Security Fixes (Week 1)

### 1.1 Implement Authentication & Authorization

Create `/Users/chungty/Projects/vdg-clean/abm-research/src/auth/auth_handler.py`:

```python
"""
JWT Authentication Handler for ABM Dashboard
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from typing import Optional, Dict, Any

class AuthHandler:
    """Handle JWT authentication and authorization"""

    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.environ.get('JWT_SECRET_KEY')
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY must be set")
        self.algorithm = 'HS256'
        self.token_expiry = timedelta(hours=24)

    def generate_token(self, user_id: str, email: str, roles: list = None) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'email': email,
            'roles': roles or ['user'],
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def jwt_required(roles: list = None):
    """Decorator to require JWT authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            auth_header = request.headers.get('Authorization')

            if auth_header:
                try:
                    token = auth_header.split(' ')[1]  # Bearer <token>
                except IndexError:
                    return jsonify({'error': 'Invalid authorization header'}), 401

            if not token:
                return jsonify({'error': 'Token missing'}), 401

            auth = AuthHandler()
            payload = auth.verify_token(token)

            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401

            # Check roles if specified
            if roles:
                user_roles = payload.get('roles', [])
                if not any(role in user_roles for role in roles):
                    return jsonify({'error': 'Insufficient permissions'}), 403

            request.user = payload
            return f(*args, **kwargs)

        return decorated_function
    return decorator
```

### 1.2 Add Input Validation & Sanitization

Create `/Users/chungty/Projects/vdg-clean/abm-research/src/utils/validators.py`:

```python
"""
Input validation and sanitization utilities
"""

import re
import html
from typing import Optional, Dict, Any
from urllib.parse import urlparse

class InputValidator:
    """Validate and sanitize user inputs"""

    @staticmethod
    def validate_domain(domain: str) -> Optional[str]:
        """Validate and sanitize domain name"""
        if not domain:
            return None

        # Remove protocol if present
        domain = domain.lower().strip()
        domain = re.sub(r'^https?://', '', domain)
        domain = domain.split('/')[0]  # Remove path

        # Validate domain format
        pattern = r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*$'

        if not re.match(pattern, domain):
            return None

        return domain

    @staticmethod
    def validate_company_name(name: str) -> Optional[str]:
        """Validate and sanitize company name"""
        if not name:
            return None

        # Remove potentially dangerous characters
        name = html.escape(name.strip())

        # Limit length
        if len(name) > 100:
            return None

        # Check for suspicious patterns
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'on\w+\s*=',
            r'data:text/html'
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return None

        return name

    @staticmethod
    def sanitize_html(text: str) -> str:
        """Sanitize HTML content to prevent XSS"""
        if not text:
            return ""

        # Escape HTML entities
        return html.escape(text)

    @staticmethod
    def validate_email(email: str) -> Optional[str]:
        """Validate email format"""
        if not email:
            return None

        email = email.lower().strip()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(pattern, email):
            return None

        return email

    @staticmethod
    def validate_uuid(uuid: str) -> Optional[str]:
        """Validate UUID format"""
        if not uuid:
            return None

        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

        if not re.match(pattern, uuid.lower()):
            return None

        return uuid

    @staticmethod
    def validate_json_input(data: Dict[str, Any], required_fields: list) -> tuple:
        """Validate JSON input has required fields"""
        missing = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing.append(field)

        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"

        return True, None
```

### 1.3 Implement Rate Limiting

Create `/Users/chungty/Projects/vdg-clean/abm-research/src/utils/rate_limiter_enhanced.py`:

```python
"""
Enhanced rate limiting with Redis support
"""

import time
from functools import wraps
from flask import request, jsonify
from collections import defaultdict
from datetime import datetime, timedelta

class EnhancedRateLimiter:
    """Enhanced rate limiter with multiple strategies"""

    def __init__(self):
        self.request_counts = defaultdict(list)
        self.blocked_ips = set()
        self.block_duration = 3600  # 1 hour

    def is_rate_limited(self, identifier: str, limit: int, window: int) -> bool:
        """Check if identifier is rate limited"""
        now = time.time()

        # Clean old requests
        self.request_counts[identifier] = [
            req_time for req_time in self.request_counts[identifier]
            if req_time > now - window
        ]

        # Check if limit exceeded
        if len(self.request_counts[identifier]) >= limit:
            return True

        # Add current request
        self.request_counts[identifier].append(now)
        return False

    def block_ip(self, ip_address: str):
        """Block an IP address temporarily"""
        self.blocked_ips.add(ip_address)

    def is_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        return ip_address in self.blocked_ips

rate_limiter = EnhancedRateLimiter()

def rate_limit(requests_per_minute: int = 60):
    """Decorator to apply rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier (IP or user ID)
            client_ip = request.remote_addr
            user_id = getattr(request, 'user', {}).get('user_id', client_ip)

            # Check if blocked
            if rate_limiter.is_blocked(client_ip):
                return jsonify({'error': 'IP temporarily blocked'}), 429

            # Check rate limit
            if rate_limiter.is_rate_limited(user_id, requests_per_minute, 60):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': 60
                }), 429

            return f(*args, **kwargs)

        return decorated_function
    return decorator
```

### 1.4 Fix XSS Vulnerabilities in Frontend

Update `/Users/chungty/Projects/vdg-clean/abm-research/unified_dashboard.html`:

Add this JavaScript security module:

```javascript
// Security utilities for XSS prevention
const Security = {
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    sanitizeUrl: function(url) {
        // Only allow http/https URLs
        try {
            const parsed = new URL(url);
            if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
                return '#';
            }
            return url;
        } catch {
            return '#';
        }
    },

    createSafeElement: function(tag, text, attributes = {}) {
        const element = document.createElement(tag);
        element.textContent = text;

        // Safely add attributes
        for (const [key, value] of Object.entries(attributes)) {
            if (key === 'href' || key === 'src') {
                element.setAttribute(key, this.sanitizeUrl(value));
            } else if (key === 'class' || key === 'id') {
                element.setAttribute(key, value);
            }
        }

        return element;
    }
};

// Replace innerHTML usage with safe DOM manipulation
function updateContactsPanel() {
    const container = document.getElementById('contacts-container');

    // Clear container safely
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }

    const contacts = dashboardData.contacts || [];

    if (contacts.length === 0) {
        const emptyState = Security.createSafeElement('div', 'No contacts found', {
            class: 'empty-state'
        });
        container.appendChild(emptyState);
        return;
    }

    // Add contacts safely
    contacts.forEach(contact => {
        const contactCard = document.createElement('div');
        contactCard.className = 'contact-card';

        const name = Security.createSafeElement('div', contact.name, {
            class: 'contact-name'
        });
        const title = Security.createSafeElement('div', contact.title, {
            class: 'contact-title'
        });

        contactCard.appendChild(name);
        contactCard.appendChild(title);
        container.appendChild(contactCard);
    });
}
```

## Priority 2: Error Handling & Logging (Week 1-2)

### 2.1 Implement Comprehensive Error Handling

Create `/Users/chungty/Projects/vdg-clean/abm-research/src/utils/error_handler.py`:

```python
"""
Centralized error handling and logging
"""

import logging
import traceback
from flask import jsonify, current_app
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('abm_dashboard.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom API exception"""
    def __init__(self, message: str, status_code: int = 500, payload: dict = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

def handle_api_error(error: APIError):
    """Handle API errors consistently"""
    response = {'error': error.message}

    # Only add debug info in development
    if current_app.debug and error.payload:
        response['debug'] = error.payload

    # Log error
    logger.error(f"API Error: {error.message}", extra={
        'status_code': error.status_code,
        'payload': error.payload
    })

    return jsonify(response), error.status_code

def handle_unexpected_error(error: Exception):
    """Handle unexpected errors"""
    # Log full stack trace
    logger.error(f"Unexpected error: {str(error)}\n{traceback.format_exc()}")

    # Return generic error to client
    response = {
        'error': 'An unexpected error occurred',
        'timestamp': datetime.utcnow().isoformat()
    }

    # Only add details in debug mode
    if current_app.debug:
        response['details'] = str(error)

    return jsonify(response), 500

def log_security_event(event_type: str, details: dict):
    """Log security-related events"""
    logger.warning(f"Security Event: {event_type}", extra={
        'event_type': event_type,
        'details': details,
        'timestamp': datetime.utcnow().isoformat()
    })
```

### 2.2 Add Database Connection Pooling

Create `/Users/chungty/Projects/vdg-clean/abm-research/src/utils/connection_pool.py`:

```python
"""
Database connection pooling for improved performance
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import requests
from typing import Optional

class NotionConnectionPool:
    """Connection pool for Notion API requests"""

    def __init__(self, max_connections: int = 10):
        self.semaphore = asyncio.Semaphore(max_connections)
        self.executor = ThreadPoolExecutor(max_workers=max_connections)
        self.session = requests.Session()
        self.session.headers.update({
            'Notion-Version': '2022-06-28'
        })

    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool"""
        async with self.semaphore:
            yield self.session

    def close(self):
        """Close the connection pool"""
        self.executor.shutdown(wait=True)
        self.session.close()

# Global connection pool
notion_pool = NotionConnectionPool()
```

## Priority 3: Monitoring & Observability (Week 2)

### 3.1 Add Health Check Endpoints

```python
# Add to unified_abm_dashboard.py

@app.route('/health')
def health_check():
    """Basic health check"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/health/detailed')
@jwt_required(roles=['admin'])
def detailed_health_check():
    """Detailed health check for monitoring"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }

    # Check Notion API
    try:
        notion_service.fetch_accounts()
        health_status['checks']['notion'] = 'healthy'
    except:
        health_status['checks']['notion'] = 'unhealthy'
        health_status['status'] = 'degraded'

    # Check memory usage
    import psutil
    memory = psutil.virtual_memory()
    health_status['checks']['memory'] = {
        'percent': memory.percent,
        'available': memory.available
    }

    return jsonify(health_status), 200 if health_status['status'] == 'healthy' else 503
```

### 3.2 Add Security Headers

```python
# Add to unified_abm_dashboard.py

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

## Testing the Hardened System

### Run Security Tests

```bash
# Run security test suite
pytest tests/test_abm_security.py -v

# Run integration tests
pytest tests/test_abm_integration.py -v

# Run OWASP ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
    -t http://localhost:8001

# Check for vulnerable dependencies
pip-audit --requirement requirements.txt

# Run bandit security linter
bandit -r src/ -f json -o security_report.json
```

### Performance Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
cat > locustfile.py << EOF
from locust import HttpUser, task, between

class ABMDashboardUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_dashboard(self):
        self.client.get("/api/data")

    @task
    def get_accounts(self):
        self.client.get("/api/accounts")
EOF

# Run load test
locust -f locustfile.py --host=http://localhost:8001
```

## Deployment Checklist

- [ ] All security tests passing
- [ ] Authentication implemented and tested
- [ ] Input validation on all endpoints
- [ ] Rate limiting configured
- [ ] XSS vulnerabilities fixed
- [ ] Error handling implemented
- [ ] Security headers added
- [ ] HTTPS enabled (production)
- [ ] Debug mode disabled (production)
- [ ] Secrets in secure vault
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Incident response plan documented

## Maintenance Schedule

### Daily
- Review security logs
- Check error rates
- Monitor API usage

### Weekly
- Run security scans
- Review rate limit violations
- Update dependencies

### Monthly
- Security audit
- Performance review
- Capacity planning

### Quarterly
- Penetration testing
- Security training
- Architecture review