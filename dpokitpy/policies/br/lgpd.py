from dpokitpy.models import ScanIssue


class LGPDPolicyBR:
    def apply(self, issue: ScanIssue) -> ScanIssue:
        if not issue.valid:
            issue.action = "warn"
            return issue

        if issue.type in ("CPF", "CNPJ", "RG", "PIS", "CNH"):
            issue.action = "block"
        elif issue.type in ("EMAIL", "PHONE"):
            issue.action = "warn"
        else:
            issue.action = "warn"

        return issue
