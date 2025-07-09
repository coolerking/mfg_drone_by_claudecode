"""
Phase 5: Audit Service for MCP Server
Provides comprehensive audit and compliance features including:
- Centralized audit logging
- Compliance reporting (SOX, HIPAA, PCI-DSS)
- Configuration change tracking
- Access pattern analysis
- Advanced threat detection
- Real-time monitoring
"""

import json
import sqlite3
import hashlib
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditEvent(Enum):
    """Audit event types"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    USER_MODIFIED = "user_modified"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    CONFIG_CHANGED = "config_changed"
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    SECURITY_EVENT = "security_event"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    COMPLIANCE_SCAN = "compliance_scan"
    AUDIT_LOG_EXPORT = "audit_log_export"


class ComplianceFramework(Enum):
    """Compliance frameworks"""
    SOX = "sox"  # Sarbanes-Oxley Act
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    GDPR = "gdpr"  # General Data Protection Regulation
    ISO_27001 = "iso_27001"  # ISO 27001
    NIST = "nist"  # NIST Cybersecurity Framework
    CIS = "cis"  # CIS Controls


class AuditLevel(Enum):
    """Audit log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditLogEntry:
    """Audit log entry"""
    id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: AuditEvent = AuditEvent.SYSTEM_STARTUP
    level: AuditLevel = AuditLevel.INFO
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    source_ip: str = "unknown"
    user_agent: str = ""
    resource: str = ""
    action: str = ""
    outcome: str = "success"
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None
    
    def __post_init__(self):
        """Generate checksum for integrity verification"""
        if self.checksum is None:
            self.checksum = self._generate_checksum()
    
    def _generate_checksum(self) -> str:
        """Generate SHA-256 checksum of the entry"""
        data = {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "level": self.level.value,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "source_ip": self.source_ip,
            "user_agent": self.user_agent,
            "resource": self.resource,
            "action": self.action,
            "outcome": self.outcome,
            "details": json.dumps(self.details, sort_keys=True),
            "metadata": json.dumps(self.metadata, sort_keys=True)
        }
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify entry integrity"""
        expected_checksum = self._generate_checksum()
        return self.checksum == expected_checksum


@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    rule_id: str
    framework: ComplianceFramework
    control_id: str
    title: str
    description: str
    severity: AuditLevel
    required_events: List[AuditEvent]
    check_function: str
    remediation: str = ""
    active: bool = True


@dataclass
class ComplianceReport:
    """Compliance report"""
    report_id: str
    framework: ComplianceFramework
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    total_rules: int
    compliant_rules: int
    non_compliant_rules: int
    compliance_percentage: float
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessPattern:
    """Access pattern analysis"""
    pattern_id: str
    user_id: str
    resource_type: str
    access_frequency: int
    access_times: List[datetime]
    locations: List[str]
    user_agents: List[str]
    risk_score: float
    anomaly_detected: bool
    pattern_description: str


class AuditService:
    """Comprehensive audit service"""
    
    def __init__(self, db_path: str = "audit_logs.db", config: Dict[str, Any] = None):
        self.db_path = Path(db_path)
        self.config = config or {}
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.access_patterns: Dict[str, List[AccessPattern]] = {}
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Initialize database
        self._init_database()
        
        # Load compliance rules
        self._load_compliance_rules()
        
        logger.info(f"Audit Service initialized with database: {self.db_path}")
    
    def _init_database(self):
        """Initialize audit database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create audit_logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        level TEXT NOT NULL,
                        user_id TEXT,
                        session_id TEXT,
                        source_ip TEXT NOT NULL,
                        user_agent TEXT,
                        resource TEXT,
                        action TEXT,
                        outcome TEXT NOT NULL,
                        details TEXT,
                        metadata TEXT,
                        checksum TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create compliance_reports table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS compliance_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        report_id TEXT UNIQUE NOT NULL,
                        framework TEXT NOT NULL,
                        generated_at TEXT NOT NULL,
                        period_start TEXT NOT NULL,
                        period_end TEXT NOT NULL,
                        total_rules INTEGER NOT NULL,
                        compliant_rules INTEGER NOT NULL,
                        non_compliant_rules INTEGER NOT NULL,
                        compliance_percentage REAL NOT NULL,
                        findings TEXT,
                        recommendations TEXT,
                        metadata TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create access_patterns table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS access_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_id TEXT UNIQUE NOT NULL,
                        user_id TEXT NOT NULL,
                        resource_type TEXT NOT NULL,
                        access_frequency INTEGER NOT NULL,
                        access_times TEXT,
                        locations TEXT,
                        user_agents TEXT,
                        risk_score REAL NOT NULL,
                        anomaly_detected BOOLEAN NOT NULL,
                        pattern_description TEXT,
                        analyzed_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create configuration_changes table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS configuration_changes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        component TEXT NOT NULL,
                        old_value TEXT,
                        new_value TEXT,
                        change_type TEXT NOT NULL,
                        approval_status TEXT DEFAULT 'pending',
                        approved_by TEXT,
                        approved_at TEXT,
                        rollback_data TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indices for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_logs(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_logs(event_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_source_ip ON audit_logs(source_ip)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_config_changes_timestamp ON configuration_changes(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_config_changes_user_id ON configuration_changes(user_id)')
                
                conn.commit()
                logger.info("Audit database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing audit database: {str(e)}")
            raise
    
    def _load_compliance_rules(self):
        """Load compliance rules"""
        # SOX compliance rules
        self.compliance_rules["sox_001"] = ComplianceRule(
            rule_id="sox_001",
            framework=ComplianceFramework.SOX,
            control_id="SOX-404",
            title="Management Assessment of Internal Controls",
            description="All configuration changes must be logged and approved",
            severity=AuditLevel.CRITICAL,
            required_events=[AuditEvent.CONFIG_CHANGED],
            check_function="check_config_change_approval",
            remediation="Ensure all configuration changes are properly approved and documented"
        )
        
        # HIPAA compliance rules
        self.compliance_rules["hipaa_001"] = ComplianceRule(
            rule_id="hipaa_001",
            framework=ComplianceFramework.HIPAA,
            control_id="HIPAA-164.312",
            title="Access Control",
            description="All access to protected health information must be logged",
            severity=AuditLevel.CRITICAL,
            required_events=[AuditEvent.DATA_ACCESS, AuditEvent.DATA_MODIFICATION],
            check_function="check_data_access_logging",
            remediation="Implement comprehensive logging for all data access events"
        )
        
        # PCI DSS compliance rules
        self.compliance_rules["pci_001"] = ComplianceRule(
            rule_id="pci_001",
            framework=ComplianceFramework.PCI_DSS,
            control_id="PCI-10.2",
            title="Audit Trail Requirements",
            description="All user activities must be logged",
            severity=AuditLevel.CRITICAL,
            required_events=[AuditEvent.USER_LOGIN, AuditEvent.USER_LOGOUT],
            check_function="check_user_activity_logging",
            remediation="Ensure all user authentication events are properly logged"
        )
        
        # GDPR compliance rules
        self.compliance_rules["gdpr_001"] = ComplianceRule(
            rule_id="gdpr_001",
            framework=ComplianceFramework.GDPR,
            control_id="GDPR-32",
            title="Security of Processing",
            description="All personal data access must be logged and monitored",
            severity=AuditLevel.CRITICAL,
            required_events=[AuditEvent.DATA_ACCESS, AuditEvent.DATA_MODIFICATION, AuditEvent.DATA_DELETION],
            check_function="check_personal_data_access",
            remediation="Implement proper logging and monitoring for personal data access"
        )
        
        logger.info(f"Loaded {len(self.compliance_rules)} compliance rules")
    
    def log_audit_event(self, event_type: AuditEvent, user_id: str = None,
                       session_id: str = None, source_ip: str = "unknown",
                       user_agent: str = "", resource: str = "", action: str = "",
                       outcome: str = "success", details: Dict[str, Any] = None,
                       metadata: Dict[str, Any] = None, level: AuditLevel = AuditLevel.INFO) -> bool:
        """Log an audit event"""
        try:
            # Create audit log entry
            entry = AuditLogEntry(
                event_type=event_type,
                level=level,
                user_id=user_id,
                session_id=session_id,
                source_ip=source_ip,
                user_agent=user_agent,
                resource=resource,
                action=action,
                outcome=outcome,
                details=details or {},
                metadata=metadata or {}
            )
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO audit_logs (
                        timestamp, event_type, level, user_id, session_id,
                        source_ip, user_agent, resource, action, outcome,
                        details, metadata, checksum
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.timestamp.isoformat(),
                    entry.event_type.value,
                    entry.level.value,
                    entry.user_id,
                    entry.session_id,
                    entry.source_ip,
                    entry.user_agent,
                    entry.resource,
                    entry.action,
                    entry.outcome,
                    json.dumps(entry.details),
                    json.dumps(entry.metadata),
                    entry.checksum
                ))
                conn.commit()
            
            # Log to system logger
            log_message = f"AUDIT: {event_type.value} - User: {user_id}, IP: {source_ip}, Outcome: {outcome}"
            
            if level == AuditLevel.CRITICAL:
                logger.critical(log_message)
            elif level == AuditLevel.ERROR:
                logger.error(log_message)
            elif level == AuditLevel.WARNING:
                logger.warning(log_message)
            else:
                logger.info(log_message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error logging audit event: {str(e)}")
            return False
    
    def track_configuration_change(self, user_id: str, component: str,
                                 old_value: Any, new_value: Any,
                                 change_type: str = "update",
                                 approval_required: bool = True) -> bool:
        """Track configuration changes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO configuration_changes (
                        timestamp, user_id, component, old_value, new_value,
                        change_type, approval_status, rollback_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.utcnow().isoformat(),
                    user_id,
                    component,
                    json.dumps(old_value) if old_value is not None else None,
                    json.dumps(new_value) if new_value is not None else None,
                    change_type,
                    "pending" if approval_required else "auto_approved",
                    json.dumps({"old_value": old_value}) if old_value is not None else None
                ))
                conn.commit()
            
            # Log audit event
            self.log_audit_event(
                AuditEvent.CONFIG_CHANGED,
                user_id=user_id,
                resource=component,
                action=change_type,
                details={
                    "old_value": old_value,
                    "new_value": new_value,
                    "approval_required": approval_required
                },
                level=AuditLevel.WARNING
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error tracking configuration change: {str(e)}")
            return False
    
    def analyze_access_patterns(self, user_id: str, days_back: int = 30) -> List[AccessPattern]:
        """Analyze user access patterns"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days_back)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT resource, source_ip, user_agent, timestamp
                    FROM audit_logs
                    WHERE user_id = ? AND timestamp BETWEEN ? AND ?
                    AND event_type IN ('data_access', 'user_login')
                    ORDER BY timestamp
                ''', (user_id, start_time.isoformat(), end_time.isoformat()))
                
                rows = cursor.fetchall()
            
            # Group by resource type
            patterns = {}
            for resource, source_ip, user_agent, timestamp in rows:
                resource_type = resource.split(':')[0] if ':' in resource else resource
                
                if resource_type not in patterns:
                    patterns[resource_type] = {
                        'access_times': [],
                        'locations': set(),
                        'user_agents': set(),
                        'count': 0
                    }
                
                patterns[resource_type]['access_times'].append(datetime.fromisoformat(timestamp))
                patterns[resource_type]['locations'].add(source_ip)
                patterns[resource_type]['user_agents'].add(user_agent)
                patterns[resource_type]['count'] += 1
            
            # Analyze patterns
            access_patterns = []
            for resource_type, data in patterns.items():
                # Calculate risk score
                risk_score = self._calculate_risk_score(data)
                
                # Detect anomalies
                anomaly_detected = self._detect_anomalies(data)
                
                pattern = AccessPattern(
                    pattern_id=f"{user_id}:{resource_type}:{int(end_time.timestamp())}",
                    user_id=user_id,
                    resource_type=resource_type,
                    access_frequency=data['count'],
                    access_times=data['access_times'],
                    locations=list(data['locations']),
                    user_agents=list(data['user_agents']),
                    risk_score=risk_score,
                    anomaly_detected=anomaly_detected,
                    pattern_description=self._generate_pattern_description(data, resource_type)
                )
                
                access_patterns.append(pattern)
                
                # Store pattern
                self._store_access_pattern(pattern)
            
            return access_patterns
            
        except Exception as e:
            logger.error(f"Error analyzing access patterns: {str(e)}")
            return []
    
    def _calculate_risk_score(self, data: Dict[str, Any]) -> float:
        """Calculate risk score for access pattern"""
        score = 0.0
        
        # Multiple locations increase risk
        if len(data['locations']) > 3:
            score += 0.3
        
        # Multiple user agents increase risk
        if len(data['user_agents']) > 2:
            score += 0.2
        
        # High frequency access
        if data['count'] > 100:
            score += 0.2
        
        # Unusual time patterns (access outside business hours)
        business_hours_access = 0
        for access_time in data['access_times']:
            if 9 <= access_time.hour <= 17:
                business_hours_access += 1
        
        if business_hours_access / len(data['access_times']) < 0.5:
            score += 0.3
        
        return min(score, 1.0)
    
    def _detect_anomalies(self, data: Dict[str, Any]) -> bool:
        """Detect anomalies in access pattern"""
        # Simple anomaly detection
        if len(data['locations']) > 5:
            return True
        
        if len(data['user_agents']) > 3:
            return True
        
        # Check for rapid successive access
        if len(data['access_times']) > 1:
            times = sorted(data['access_times'])
            rapid_access = 0
            for i in range(1, len(times)):
                if (times[i] - times[i-1]).seconds < 60:
                    rapid_access += 1
            
            if rapid_access > len(times) * 0.5:
                return True
        
        return False
    
    def _generate_pattern_description(self, data: Dict[str, Any], resource_type: str) -> str:
        """Generate human-readable pattern description"""
        desc = f"User accessed {resource_type} {data['count']} times"
        
        if len(data['locations']) > 1:
            desc += f" from {len(data['locations'])} different locations"
        
        if len(data['user_agents']) > 1:
            desc += f" using {len(data['user_agents'])} different user agents"
        
        return desc
    
    def _store_access_pattern(self, pattern: AccessPattern):
        """Store access pattern in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO access_patterns (
                        pattern_id, user_id, resource_type, access_frequency,
                        access_times, locations, user_agents, risk_score,
                        anomaly_detected, pattern_description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern.pattern_id,
                    pattern.user_id,
                    pattern.resource_type,
                    pattern.access_frequency,
                    json.dumps([t.isoformat() for t in pattern.access_times]),
                    json.dumps(pattern.locations),
                    json.dumps(pattern.user_agents),
                    pattern.risk_score,
                    pattern.anomaly_detected,
                    pattern.pattern_description
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing access pattern: {str(e)}")
    
    def generate_compliance_report(self, framework: ComplianceFramework,
                                 period_start: datetime, period_end: datetime) -> ComplianceReport:
        """Generate compliance report"""
        try:
            report_id = f"{framework.value}_{int(datetime.utcnow().timestamp())}"
            
            # Get relevant compliance rules
            framework_rules = [
                rule for rule in self.compliance_rules.values()
                if rule.framework == framework and rule.active
            ]
            
            findings = []
            compliant_rules = 0
            
            for rule in framework_rules:
                compliance_result = self._check_rule_compliance(rule, period_start, period_end)
                findings.append(compliance_result)
                
                if compliance_result['compliant']:
                    compliant_rules += 1
            
            non_compliant_rules = len(framework_rules) - compliant_rules
            compliance_percentage = (compliant_rules / len(framework_rules)) * 100 if framework_rules else 0
            
            # Generate recommendations
            recommendations = self._generate_compliance_recommendations(findings)
            
            report = ComplianceReport(
                report_id=report_id,
                framework=framework,
                generated_at=datetime.utcnow(),
                period_start=period_start,
                period_end=period_end,
                total_rules=len(framework_rules),
                compliant_rules=compliant_rules,
                non_compliant_rules=non_compliant_rules,
                compliance_percentage=compliance_percentage,
                findings=findings,
                recommendations=recommendations
            )
            
            # Store report
            self._store_compliance_report(report)
            
            # Log audit event
            self.log_audit_event(
                AuditEvent.COMPLIANCE_SCAN,
                resource=framework.value,
                action="generate_report",
                details={
                    "report_id": report_id,
                    "compliance_percentage": compliance_percentage,
                    "total_rules": len(framework_rules)
                },
                level=AuditLevel.INFO
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {str(e)}")
            raise
    
    def _check_rule_compliance(self, rule: ComplianceRule, 
                             period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Check compliance for a specific rule"""
        try:
            # Check if required events are present
            required_events_present = True
            missing_events = []
            
            for event_type in rule.required_events:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT COUNT(*) FROM audit_logs
                        WHERE event_type = ? AND timestamp BETWEEN ? AND ?
                    ''', (event_type.value, period_start.isoformat(), period_end.isoformat()))
                    
                    count = cursor.fetchone()[0]
                    if count == 0:
                        required_events_present = False
                        missing_events.append(event_type.value)
            
            # Additional compliance checks based on rule
            additional_checks = self._perform_additional_compliance_checks(rule, period_start, period_end)
            
            return {
                'rule_id': rule.rule_id,
                'control_id': rule.control_id,
                'title': rule.title,
                'compliant': required_events_present and additional_checks['compliant'],
                'missing_events': missing_events,
                'additional_findings': additional_checks['findings'],
                'severity': rule.severity.value,
                'remediation': rule.remediation
            }
            
        except Exception as e:
            logger.error(f"Error checking rule compliance: {str(e)}")
            return {
                'rule_id': rule.rule_id,
                'compliant': False,
                'error': str(e)
            }
    
    def _perform_additional_compliance_checks(self, rule: ComplianceRule,
                                           period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Perform additional compliance checks"""
        findings = []
        compliant = True
        
        try:
            if rule.check_function == "check_config_change_approval":
                # Check if configuration changes are approved
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT COUNT(*) FROM configuration_changes
                        WHERE timestamp BETWEEN ? AND ? AND approval_status = 'pending'
                    ''', (period_start.isoformat(), period_end.isoformat()))
                    
                    pending_changes = cursor.fetchone()[0]
                    if pending_changes > 0:
                        compliant = False
                        findings.append(f"{pending_changes} configuration changes pending approval")
            
            elif rule.check_function == "check_data_access_logging":
                # Check if data access is properly logged
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT COUNT(*) FROM audit_logs
                        WHERE event_type IN ('data_access', 'data_modification')
                        AND timestamp BETWEEN ? AND ?
                        AND details IS NULL
                    ''', (period_start.isoformat(), period_end.isoformat()))
                    
                    incomplete_logs = cursor.fetchone()[0]
                    if incomplete_logs > 0:
                        compliant = False
                        findings.append(f"{incomplete_logs} data access events with incomplete logging")
            
            return {
                'compliant': compliant,
                'findings': findings
            }
            
        except Exception as e:
            logger.error(f"Error performing additional compliance checks: {str(e)}")
            return {
                'compliant': False,
                'findings': [f"Error during compliance check: {str(e)}"]
            }
    
    def _generate_compliance_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        non_compliant_findings = [f for f in findings if not f.get('compliant', False)]
        
        if non_compliant_findings:
            recommendations.append("Address non-compliant rules immediately")
            
            # Group by severity
            critical_findings = [f for f in non_compliant_findings if f.get('severity') == 'critical']
            if critical_findings:
                recommendations.append("Focus on critical severity findings first")
            
            # Common recommendations
            if any('missing_events' in f for f in non_compliant_findings):
                recommendations.append("Implement comprehensive audit logging for all required events")
            
            if any('approval' in str(f.get('additional_findings', [])) for f in non_compliant_findings):
                recommendations.append("Establish proper approval workflows for configuration changes")
        
        else:
            recommendations.append("Compliance posture is good - maintain current controls")
        
        return recommendations
    
    def _store_compliance_report(self, report: ComplianceReport):
        """Store compliance report in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO compliance_reports (
                        report_id, framework, generated_at, period_start, period_end,
                        total_rules, compliant_rules, non_compliant_rules,
                        compliance_percentage, findings, recommendations, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    report.report_id,
                    report.framework.value,
                    report.generated_at.isoformat(),
                    report.period_start.isoformat(),
                    report.period_end.isoformat(),
                    report.total_rules,
                    report.compliant_rules,
                    report.non_compliant_rules,
                    report.compliance_percentage,
                    json.dumps(report.findings),
                    json.dumps(report.recommendations),
                    json.dumps(report.metadata)
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing compliance report: {str(e)}")
    
    def export_audit_logs(self, format: str = "json", period_start: datetime = None,
                         period_end: datetime = None, filters: Dict[str, Any] = None) -> str:
        """Export audit logs"""
        try:
            if period_start is None:
                period_start = datetime.utcnow() - timedelta(days=30)
            if period_end is None:
                period_end = datetime.utcnow()
            
            # Build query
            query = "SELECT * FROM audit_logs WHERE timestamp BETWEEN ? AND ?"
            params = [period_start.isoformat(), period_end.isoformat()]
            
            if filters:
                if 'user_id' in filters:
                    query += " AND user_id = ?"
                    params.append(filters['user_id'])
                if 'event_type' in filters:
                    query += " AND event_type = ?"
                    params.append(filters['event_type'])
                if 'source_ip' in filters:
                    query += " AND source_ip = ?"
                    params.append(filters['source_ip'])
            
            query += " ORDER BY timestamp DESC"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
            
            # Convert to desired format
            if format.lower() == "json":
                data = []
                for row in rows:
                    record = dict(zip(columns, row))
                    # Parse JSON fields
                    if record['details']:
                        record['details'] = json.loads(record['details'])
                    if record['metadata']:
                        record['metadata'] = json.loads(record['metadata'])
                    data.append(record)
                
                result = json.dumps(data, indent=2, default=str)
            
            elif format.lower() == "csv":
                import csv
                from io import StringIO
                
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(columns)
                writer.writerows(rows)
                result = output.getvalue()
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            # Log export event
            self.log_audit_event(
                AuditEvent.AUDIT_LOG_EXPORT,
                action=f"export_{format}",
                details={
                    "period_start": period_start.isoformat(),
                    "period_end": period_end.isoformat(),
                    "record_count": len(rows),
                    "filters": filters or {}
                },
                level=AuditLevel.INFO
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error exporting audit logs: {str(e)}")
            raise
    
    def start_continuous_monitoring(self):
        """Start continuous monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._continuous_monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("Continuous monitoring started")
    
    def stop_continuous_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        logger.info("Continuous monitoring stopped")
    
    def _continuous_monitor(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                # Check for suspicious patterns
                self._check_suspicious_patterns()
                
                # Check for compliance violations
                self._check_realtime_compliance()
                
                # Clean up old logs
                self._cleanup_old_logs()
                
                # Sleep for 5 minutes
                import time
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {str(e)}")
                import time
                time.sleep(60)
    
    def _check_suspicious_patterns(self):
        """Check for suspicious patterns"""
        try:
            # Check for rapid login attempts
            current_time = datetime.utcnow()
            five_minutes_ago = current_time - timedelta(minutes=5)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT source_ip, COUNT(*) as attempt_count
                    FROM audit_logs
                    WHERE event_type = 'user_login' AND outcome = 'failure'
                    AND timestamp > ?
                    GROUP BY source_ip
                    HAVING attempt_count > 5
                ''', (five_minutes_ago.isoformat(),))
                
                suspicious_ips = cursor.fetchall()
            
            for ip, count in suspicious_ips:
                self.log_audit_event(
                    AuditEvent.SECURITY_EVENT,
                    source_ip=ip,
                    action="suspicious_login_pattern",
                    details={
                        "failed_attempts": count,
                        "time_window": "5_minutes"
                    },
                    level=AuditLevel.WARNING
                )
                
        except Exception as e:
            logger.error(f"Error checking suspicious patterns: {str(e)}")
    
    def _check_realtime_compliance(self):
        """Check for real-time compliance violations"""
        try:
            # Check for unapproved configuration changes
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM configuration_changes
                    WHERE approval_status = 'pending'
                    AND timestamp < ?
                ''', ((datetime.utcnow() - timedelta(hours=1)).isoformat(),))
                
                pending_changes = cursor.fetchone()[0]
            
            if pending_changes > 0:
                self.log_audit_event(
                    AuditEvent.COMPLIANCE_SCAN,
                    action="compliance_violation",
                    details={
                        "violation_type": "unapproved_config_changes",
                        "pending_count": pending_changes
                    },
                    level=AuditLevel.WARNING
                )
                
        except Exception as e:
            logger.error(f"Error checking real-time compliance: {str(e)}")
    
    def _cleanup_old_logs(self):
        """Clean up old audit logs"""
        try:
            # Keep logs for 1 year by default
            cutoff_date = datetime.utcnow() - timedelta(days=365)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM audit_logs
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old audit log entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {str(e)}")
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """Get audit statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total logs
                cursor.execute("SELECT COUNT(*) FROM audit_logs")
                total_logs = cursor.fetchone()[0]
                
                # Logs by event type
                cursor.execute('''
                    SELECT event_type, COUNT(*) as count
                    FROM audit_logs
                    GROUP BY event_type
                    ORDER BY count DESC
                ''')
                logs_by_type = dict(cursor.fetchall())
                
                # Logs by level
                cursor.execute('''
                    SELECT level, COUNT(*) as count
                    FROM audit_logs
                    GROUP BY level
                    ORDER BY count DESC
                ''')
                logs_by_level = dict(cursor.fetchall())
                
                # Recent activity
                cursor.execute('''
                    SELECT COUNT(*) FROM audit_logs
                    WHERE timestamp > ?
                ''', ((datetime.utcnow() - timedelta(hours=24)).isoformat(),))
                recent_activity = cursor.fetchone()[0]
                
                return {
                    "total_logs": total_logs,
                    "logs_by_type": logs_by_type,
                    "logs_by_level": logs_by_level,
                    "recent_activity_24h": recent_activity,
                    "monitoring_active": self.monitoring_active
                }
                
        except Exception as e:
            logger.error(f"Error getting audit statistics: {str(e)}")
            return {}


# Example usage
if __name__ == "__main__":
    # Create audit service
    audit_service = AuditService()
    
    # Log some events
    audit_service.log_audit_event(
        AuditEvent.USER_LOGIN,
        user_id="user123",
        source_ip="192.168.1.100",
        outcome="success"
    )
    
    audit_service.log_audit_event(
        AuditEvent.CONFIG_CHANGED,
        user_id="admin",
        resource="security_config",
        action="update",
        details={"field": "mfa_required", "old_value": False, "new_value": True}
    )
    
    # Generate compliance report
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()
    
    sox_report = audit_service.generate_compliance_report(
        ComplianceFramework.SOX,
        start_date,
        end_date
    )
    
    print(f"SOX Compliance: {sox_report.compliance_percentage:.1f}%")
    
    # Analyze access patterns
    patterns = audit_service.analyze_access_patterns("user123")
    print(f"Found {len(patterns)} access patterns")
    
    # Start monitoring
    audit_service.start_continuous_monitoring()
    
    # Get statistics
    stats = audit_service.get_audit_statistics()
    print(f"Total audit logs: {stats['total_logs']}")