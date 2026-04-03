import hashlib
from datetime import datetime


class AuditLogger:
    def build_record(self, original_text: str, masked_text: str, result, country: str) -> dict:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "country": country,
            "total_issues": result.total_issues,
            "original_text_hash": self._hash_text(original_text),
            "masked_text_hash": self._hash_text(masked_text)
        }

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
