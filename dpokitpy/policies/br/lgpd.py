from dpokitpy.models import ScanIssue


class LGPDPolicyBR:
    def apply(self, issue: ScanIssue) -> ScanIssue:
        if not issue.valid:
            issue.action = "ignore"
            return issue

        if issue.type == "CPF":
            issue.action = "block"
        elif issue.type == "CNPJ":
            issue.action = "block"
        elif issue.type == "EMAIL":
            issue.action = "warn"
        elif issue.type == "PHONE":
            issue.action = "warn"
        else:
            issue.action = "ignore"

        return issue
