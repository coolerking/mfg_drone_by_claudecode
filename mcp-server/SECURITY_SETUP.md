# Security Setup Guide

## ⚠️ Critical Security Fixes Applied

This document describes the security vulnerabilities that have been fixed and how to configure the system securely.

## Fixed Vulnerabilities

### 1. ❌ Hardcoded JWT Secrets (FIXED ✅)

**Problem**: JWT secrets were hardcoded in multiple files:
- `security_manager.py`: `jwt_secret: str = "your-secret-key"`
- `phase5_main.py`: `jwt_secret=os.getenv("JWT_SECRET", "your-secure-secret-key")`
- `start_phase5_mcp_server.py`: `jwt_secret=os.getenv("JWT_SECRET", "your-secure-secret-key-change-in-production")`

**Fix**: 
- Removed all hardcoded fallback values
- Added validation to reject weak/default secrets
- Made JWT_SECRET environment variable mandatory
- Added minimum length requirement (32 characters)

### 2. ❌ Hardcoded Login Credentials (FIXED ✅)

**Problem**: Login credentials were hardcoded in `phase5_main.py`:
```python
if username == "admin" and password == "admin123":
elif username == "operator" and password == "operator123":
```

**Fix**:
- Replaced with environment variable-based authentication
- Added support for multiple user types (admin, operator, readonly)
- Implemented proper security validation
- Added account lockout and rate limiting

## Required Environment Variables

### Critical Security Settings (REQUIRED)

```bash
# JWT Secret (REQUIRED - minimum 32 characters)
JWT_SECRET=your-strong-jwt-secret-here-must-be-at-least-32-chars-long

# At least one user must be configured:
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-secure-admin-password

# Optional additional users:
OPERATOR_USERNAME=your-operator-username
OPERATOR_PASSWORD=your-secure-operator-password

READONLY_USERNAME=your-readonly-username
READONLY_PASSWORD=your-secure-readonly-password
```

### Optional Security Settings

```bash
# Environment (affects validation strictness)
ENVIRONMENT=development  # or 'production'

# JWT Settings
JWT_EXPIRY_MINUTES=60

# Account Security
MAX_FAILED_ATTEMPTS=5
LOCKOUT_DURATION=15

# IP Access Control
ALLOWED_IPS=192.168.1.0/24,10.0.0.0/8  # comma-separated
BLOCKED_IPS=192.168.1.100,10.0.0.50    # comma-separated

# Monitoring
ENABLE_MONITORING=true
MONITORING_INTERVAL=30
ENABLE_AUDIT_LOGGING=true
```

## Security Setup Instructions

### Step 1: Generate Secure Secrets

```bash
# Generate JWT secret (64+ characters recommended)
openssl rand -base64 64

# Alternative using Python
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate secure passwords
openssl rand -base64 32
```

### Step 2: Create Environment Configuration

Create a `.env` file in the mcp-server directory:

```bash
# Copy the example and customize
cp .env.example .env
# Edit .env with your secure values
```

### Step 3: Validate Configuration

```bash
# Test your configuration
python start_phase5_mcp_server.py --validate-config

# Run health checks
python start_phase5_mcp_server.py --health-check
```

### Step 4: Test Security Implementation

```bash
# Run security validation tests
cd tests
python test_security_fixes.py
```

## Security Features Implemented

### ✅ Authentication & Authorization
- Environment variable-based user credentials
- Multi-level security roles (Admin, Operator, Read-only)
- JWT token-based authentication
- API key authentication
- Session management with expiry

### ✅ Protection Mechanisms
- Account lockout after failed attempts
- Rate limiting per user/IP
- IP allowlist/blocklist support
- Input validation and sanitization
- Protection against injection attacks

### ✅ Monitoring & Auditing
- Security event logging
- Threat analysis and reporting
- Real-time security metrics
- Failed attempt tracking
- Comprehensive audit trails

### ✅ Configuration Validation
- Mandatory security settings
- Weak credential detection
- JWT secret strength validation
- Environment-specific requirements

## Production Deployment

### Requirements for Production

1. **Set ENVIRONMENT=production**
2. **Configure all required environment variables**
3. **Use strong, unique credentials**
4. **Enable IP access controls**
5. **Set up SSL/TLS (reverse proxy recommended)**
6. **Monitor security logs regularly**

### Recommended Production Setup

```bash
# Production environment
ENVIRONMENT=production

# Strong JWT secret (64+ characters)
JWT_SECRET=<generated-64-character-secret>

# Secure admin credentials
ADMIN_USERNAME=<unique-admin-username>
ADMIN_PASSWORD=<strong-admin-password>

# Operator credentials
OPERATOR_USERNAME=<unique-operator-username>
OPERATOR_PASSWORD=<strong-operator-password>

# IP restrictions
ALLOWED_IPS=10.0.0.0/8,192.168.0.0/16

# Enhanced security settings
MAX_FAILED_ATTEMPTS=3
LOCKOUT_DURATION=30
JWT_EXPIRY_MINUTES=30

# Full monitoring
ENABLE_MONITORING=true
ENABLE_AUDIT_LOGGING=true
```

## Security Testing

### Run Complete Security Test Suite

```bash
# Test all security fixes
pytest tests/test_security_fixes.py -v

# Test general functionality  
pytest tests/test_phase5_integration.py -v
```

### Manual Security Testing

1. **Test weak JWT secret rejection**:
   ```bash
   JWT_SECRET="weak" python start_phase5_mcp_server.py --validate-config
   # Should fail with validation error
   ```

2. **Test missing credentials**:
   ```bash
   # Remove all user env vars
   python start_phase5_mcp_server.py --validate-config
   # Should fail with user configuration error
   ```

3. **Test authentication endpoints**:
   ```bash
   # Start server and test login
   curl -X POST http://localhost:8003/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "wrong"}'
   # Should return 401 Unauthorized
   ```

## Migration from Previous Versions

If upgrading from a previous version with hardcoded credentials:

1. **Stop the server**
2. **Set up environment variables** as described above
3. **Test configuration** with `--validate-config`
4. **Restart server** and verify functionality
5. **Update any scripts** that relied on hardcoded credentials

## Security Monitoring

### Key Metrics to Monitor

- Failed authentication attempts
- Account lockouts
- Rate limit violations
- Suspicious IP activity
- Security event trends

### Alert Thresholds

- **Critical**: Failed admin login attempts
- **High**: Multiple account lockouts
- **Medium**: Rate limit violations
- **Low**: Successful admin logins

## Support and Security Reporting

For security issues or questions:

1. **Configuration issues**: Check this documentation
2. **Security vulnerabilities**: Report privately to maintainers
3. **General questions**: Use project issue tracker

---

**⚠️ Security Reminder**: Never commit `.env` files or real credentials to version control!