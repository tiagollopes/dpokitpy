from dpokitpy.scanner import Scanner
from dpokitpy.masker import Masker
from dpokitpy.audit_logger import AuditLogger


class Guard:
    def __init__(self, country: str = "BR"):
        self.country = country.upper()
        self.scanner = Scanner(country=self.country)
        self.masker = Masker()
        self.audit_logger = AuditLogger()

    def validate(self, text: str):
        result = self.scanner.scan(text)
        result.masked_text = self.masker.mask(text, result.issues)
        result.audit_record = self.audit_logger.build_record(
            original_text=text,
            masked_text=result.masked_text,
            result=result,
            country=self.country
        )
        return result

    #def find(self, text: str):
    #    result = self.validate(text)
    #    return result.issues

    def find(self, text: str):
        result = self.validate(text)
        return [issue.to_dict() for issue in result.issues]

    def mask(self, text: str):
        result = self.validate(text)
        return result.masked_text

    def is_safe(self, text: str, risk: str | None = None) -> bool:
        result = self.validate(text)

        valid_issues = [issue for issue in result.issues if issue.valid]

        if risk is None:
            return len(valid_issues) == 0

        risk = risk.lower()

        filtered_issues = [
            issue for issue in valid_issues
            if issue.risk.lower() == risk
        ]

    def hash_original(self, text: str) -> str:
        """Retorna o SHA-256 do texto bruto enviado."""
        result = self.validate(text)
        return result.audit_record.get("original_text_hash")

    def hash_masked(self, text: str) -> str:
        """Retorna o SHA-256 do texto após a aplicação das máscaras."""
        result = self.validate(text)
        return result.audit_record.get("masked_text_hash")

        return len(filtered_issues) == 0
