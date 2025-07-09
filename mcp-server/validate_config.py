#!/usr/bin/env python3
"""
Configuration validation script for MCP Server
Validates security settings and environment configuration
"""

import os
import sys
import argparse
from typing import List, Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings, settings


def validate_jwt_secret(jwt_secret: str) -> List[str]:
    """Validate JWT secret strength"""
    errors = []
    
    if not jwt_secret:
        errors.append("JWT_SECRET is required")
        return errors
    
    if len(jwt_secret) < 32:
        errors.append(f"JWT_SECRET must be at least 32 characters long (current: {len(jwt_secret)})")
    
    # Check for weak secrets
    weak_secrets = [
        "your-secret-key",
        "your-secure-secret-key", 
        "your-secure-secret-key-change-in-production",
        "secret",
        "password",
        "admin",
        "test",
        "12345",
        "changeme"
    ]
    
    if jwt_secret.lower() in [s.lower() for s in weak_secrets]:
        errors.append("JWT_SECRET is using a weak/default value")
    
    return errors


def validate_passwords(settings: Settings) -> List[str]:
    """Validate authentication passwords"""
    errors = []
    
    if not settings.admin_password:
        errors.append("ADMIN_PASSWORD is required")
    elif len(settings.admin_password) < 8:
        errors.append("ADMIN_PASSWORD must be at least 8 characters long")
    
    if not settings.operator_password:
        errors.append("OPERATOR_PASSWORD is required")
    elif len(settings.operator_password) < 8:
        errors.append("OPERATOR_PASSWORD must be at least 8 characters long")
    
    if not settings.readonly_password:
        errors.append("READONLY_PASSWORD is required")
    elif len(settings.readonly_password) < 8:
        errors.append("READONLY_PASSWORD must be at least 8 characters long")
    
    return errors


def validate_ssl_configuration(settings: Settings) -> List[str]:
    """Validate SSL/TLS configuration"""
    errors = []
    
    if settings.ssl_enabled:
        if not settings.ssl_cert_path:
            errors.append("SSL_CERT_PATH is required when SSL is enabled")
        elif not os.path.exists(settings.ssl_cert_path):
            errors.append(f"SSL certificate file not found: {settings.ssl_cert_path}")
        
        if not settings.ssl_key_path:
            errors.append("SSL_KEY_PATH is required when SSL is enabled")
        elif not os.path.exists(settings.ssl_key_path):
            errors.append(f"SSL key file not found: {settings.ssl_key_path}")
    
    return errors


def validate_cors_configuration(settings: Settings) -> List[str]:
    """Validate CORS configuration"""
    errors = []
    
    if settings.is_production() and "*" in settings.allowed_origins:
        errors.append("CORS wildcard (*) is not allowed in production environment")
    
    return errors


def validate_trusted_hosts(settings: Settings) -> List[str]:
    """Validate trusted hosts configuration"""
    errors = []
    
    if settings.trusted_hosts_enabled:
        if not settings.trusted_hosts:
            errors.append("TRUSTED_HOSTS must be configured when enabled")
        elif settings.is_production() and "*" in settings.trusted_hosts:
            errors.append("Trusted hosts wildcard (*) is not allowed in production environment")
    
    return errors


def validate_log_configuration(settings: Settings) -> List[str]:
    """Validate logging configuration"""
    errors = []
    
    if settings.log_file:
        log_dir = os.path.dirname(settings.log_file)
        if log_dir and not os.path.exists(log_dir):
            errors.append(f"Log directory does not exist: {log_dir}")
    
    if settings.audit_log_file:
        audit_log_dir = os.path.dirname(settings.audit_log_file)
        if audit_log_dir and not os.path.exists(audit_log_dir):
            errors.append(f"Audit log directory does not exist: {audit_log_dir}")
    
    return errors


def validate_production_readiness(settings: Settings) -> List[str]:
    """Validate production readiness"""
    errors = []
    
    if not settings.is_production():
        return errors
    
    # Production-specific checks
    if settings.debug:
        errors.append("Debug mode should be disabled in production")
    
    if not settings.ssl_enabled:
        errors.append("SSL/TLS should be enabled in production")
    
    if not settings.force_https:
        errors.append("HTTPS should be forced in production")
    
    if not settings.security_headers_enabled:
        errors.append("Security headers should be enabled in production")
    
    return errors


def generate_security_report(settings: Settings) -> Dict[str, Any]:
    """Generate a comprehensive security report"""
    report = {
        "environment": settings.environment,
        "security_score": 0,
        "max_score": 100,
        "checks": {},
        "recommendations": []
    }
    
    # JWT Secret validation
    jwt_errors = validate_jwt_secret(settings.jwt_secret or "")
    report["checks"]["jwt_secret"] = {
        "status": "PASS" if not jwt_errors else "FAIL",
        "errors": jwt_errors,
        "score": 15 if not jwt_errors else 0
    }
    
    # Password validation
    password_errors = validate_passwords(settings)
    report["checks"]["passwords"] = {
        "status": "PASS" if not password_errors else "FAIL",
        "errors": password_errors,
        "score": 20 if not password_errors else 0
    }
    
    # SSL configuration
    ssl_errors = validate_ssl_configuration(settings)
    report["checks"]["ssl"] = {
        "status": "PASS" if not ssl_errors else "FAIL",
        "errors": ssl_errors,
        "score": 15 if not ssl_errors else 0
    }
    
    # CORS configuration
    cors_errors = validate_cors_configuration(settings)
    report["checks"]["cors"] = {
        "status": "PASS" if not cors_errors else "FAIL",
        "errors": cors_errors,
        "score": 10 if not cors_errors else 0
    }
    
    # Trusted hosts
    trusted_hosts_errors = validate_trusted_hosts(settings)
    report["checks"]["trusted_hosts"] = {
        "status": "PASS" if not trusted_hosts_errors else "FAIL",
        "errors": trusted_hosts_errors,
        "score": 10 if not trusted_hosts_errors else 0
    }
    
    # Logging configuration
    log_errors = validate_log_configuration(settings)
    report["checks"]["logging"] = {
        "status": "PASS" if not log_errors else "FAIL",
        "errors": log_errors,
        "score": 10 if not log_errors else 0
    }
    
    # Production readiness
    production_errors = validate_production_readiness(settings)
    report["checks"]["production"] = {
        "status": "PASS" if not production_errors else "FAIL",
        "errors": production_errors,
        "score": 20 if not production_errors else 0
    }
    
    # Calculate total score
    report["security_score"] = sum(check["score"] for check in report["checks"].values())
    
    # Generate recommendations
    if report["security_score"] < 70:
        report["recommendations"].append("Security score is below 70%. Review and fix failing checks.")
    
    if settings.is_production() and report["security_score"] < 90:
        report["recommendations"].append("Production environment should have security score above 90%.")
    
    return report


def main():
    parser = argparse.ArgumentParser(description="Validate MCP Server configuration")
    parser.add_argument("--env-file", help="Path to environment file", default=".env")
    parser.add_argument("--report", action="store_true", help="Generate security report")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--fail-on-error", action="store_true", help="Exit with non-zero code on validation errors")
    
    args = parser.parse_args()
    
    # Load settings
    if args.env_file and os.path.exists(args.env_file):
        os.environ.setdefault("ENV_FILE", args.env_file)
    
    try:
        config = Settings()
        
        if args.report:
            report = generate_security_report(config)
            
            if args.json:
                import json
                print(json.dumps(report, indent=2))
            else:
                print(f"Security Report for {config.environment.upper()} environment")
                print("=" * 60)
                print(f"Security Score: {report['security_score']}/{report['max_score']}")
                print()
                
                for check_name, check_data in report["checks"].items():
                    status_icon = "✓" if check_data["status"] == "PASS" else "✗"
                    print(f"{status_icon} {check_name.replace('_', ' ').title()}: {check_data['status']} ({check_data['score']}/15-20)")
                    
                    if check_data["errors"]:
                        for error in check_data["errors"]:
                            print(f"  - {error}")
                    print()
                
                if report["recommendations"]:
                    print("Recommendations:")
                    for rec in report["recommendations"]:
                        print(f"  - {rec}")
        else:
            # Simple validation
            print("Validating MCP Server configuration...")
            print(f"Environment: {config.environment}")
            
            all_errors = []
            
            # Run all validation checks
            all_errors.extend(validate_jwt_secret(config.jwt_secret or ""))
            all_errors.extend(validate_passwords(config))
            all_errors.extend(validate_ssl_configuration(config))
            all_errors.extend(validate_cors_configuration(config))
            all_errors.extend(validate_trusted_hosts(config))
            all_errors.extend(validate_log_configuration(config))
            all_errors.extend(validate_production_readiness(config))
            
            if all_errors:
                print(f"\nValidation failed with {len(all_errors)} errors:")
                for error in all_errors:
                    print(f"  - {error}")
                
                if args.fail_on_error:
                    sys.exit(1)
            else:
                print("\nConfiguration validation passed!")
                
    except Exception as e:
        print(f"Error loading configuration: {e}")
        if args.fail_on_error:
            sys.exit(1)


if __name__ == "__main__":
    main()