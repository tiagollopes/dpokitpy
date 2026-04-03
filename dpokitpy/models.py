class ScanIssue:
    def __init__(
        self,
        type: str,
        value: str,
        valid: bool,
        risk: str,
        reason: str,
        action: str = "ignore"
    ):
        self.type = type
        self.value = value
        self.valid = valid
        self.risk = risk
        self.reason = reason
        self.action = action

    def to_dict(self):
        return {
            "type": self.type,
            "value": self.value,
            "valid": self.valid,
            "risk": self.risk,
            "reason": self.reason,
            "action": self.action
        }

    def __repr__(self):
        return f"ScanIssue({self.to_dict()})"


class ScanResult:
    def __init__(self, issues: list, masked_text: str = "", audit_record: dict | None = None):
        self.issues = issues
        self.total_issues = len(issues)
        self.is_safe = len(issues) == 0
        self.masked_text = masked_text
        self.audit_record = audit_record or {}

    def to_dict(self):
        return {
            "is_safe": self.is_safe,
            "total_issues": self.total_issues,
            "issues": [issue.to_dict() for issue in self.issues],
            "masked_text": self.masked_text,
            "audit_record": self.audit_record
        }

    def __repr__(self):
        return f"ScanResult({self.to_dict()})"
