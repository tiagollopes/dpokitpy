from dpokitpy.models import ScanIssue, ScanResult
from dpokitpy.validators.br.cpf import find_cpfs, is_valid_cpf
from dpokitpy.validators.br.cnpj import find_cnpjs, is_valid_cnpj
from dpokitpy.validators.br.email import find_emails, is_valid_email
from dpokitpy.validators.br.phone import find_phones, is_valid_phone
from dpokitpy.validators.br.pis import find_pis, is_valid_pis
from dpokitpy.validators.br.cnh import find_cnhs, is_valid_cnh
from dpokitpy.validators.br.rg import find_rgs, is_valid_rg
from dpokitpy.policies.br.lgpd import LGPDPolicyBR


class Scanner:
    def __init__(self, country: str = "BR"):
        self.country = country.upper()

        if self.country == "BR":
            self.policy = LGPDPolicyBR()
        else:
            self.policy = None

    def _build_issues(
        self,
        issue_type: str,
        matches: list[str],
        validator,
        valid_risk: str,
        valid_reason: str,
        invalid_risk: str,
        invalid_reason: str
    ) -> list[ScanIssue]:
        issues = []

        for value in matches:
            is_valid = validator(value)

            if is_valid:
                risk = valid_risk
                reason = valid_reason
            else:
                risk = invalid_risk
                reason = invalid_reason

            issue = ScanIssue(
                type=issue_type,
                value=value,
                valid=is_valid,
                risk=risk,
                reason=reason
            )

            if self.policy is not None:
                issue = self.policy.apply(issue)

            issues.append(issue)

        return issues

    def scan(self, text: str):
        issues = []

        if self.country == "BR":
            cpf_matches = find_cpfs(text)
            cnpj_matches = find_cnpjs(text)
            email_matches = find_emails(text)
            phone_matches = find_phones(text)
            pis_matches = find_pis(text)
            cnh_matches = find_cnhs(text)
            rg_matches = find_rgs(text)

            issues.extend(
                self._build_issues(
                    issue_type="CPF",
                    matches=cpf_matches,
                    validator=is_valid_cpf,
                    valid_risk="high",
                    valid_reason="CPF válido encontrado no texto.",
                    invalid_risk="medium",
                    invalid_reason="CPF inválido."
                )
            )

            issues.extend(
                self._build_issues(
                    issue_type="CNPJ",
                    matches=cnpj_matches,
                    validator=is_valid_cnpj,
                    valid_risk="high",
                    valid_reason="CNPJ válido encontrado no texto.",
                    invalid_risk="medium",
                    invalid_reason="CNPJ inválido."
                )
            )

            issues.extend(
                self._build_issues(
                    issue_type="EMAIL",
                    matches=email_matches,
                    validator=is_valid_email,
                    valid_risk="medium",
                    valid_reason="Email encontrado no texto.",
                    invalid_risk="low",
                    invalid_reason="Email inválido."
                )
            )

            issues.extend(
                self._build_issues(
                    issue_type="PHONE",
                    matches=phone_matches,
                    validator=is_valid_phone,
                    valid_risk="medium",
                    valid_reason="Telefone encontrado no texto.",
                    invalid_risk="low",
                    invalid_reason="Telefone inválido."
                )
            )

            issues.extend(
                self._build_issues(
                    issue_type="PIS",
                    matches=pis_matches,
                    validator=is_valid_pis,
                    valid_risk="high",
                    valid_reason="PIS válido encontrado no texto.",
                    invalid_risk="medium",
                    invalid_reason="PIS inválido."
                )
            )

            issues.extend(
                self._build_issues(
                    issue_type="CNH",
                    matches=cnh_matches,
                    validator=is_valid_cnh,
                    valid_risk="high",
                    valid_reason="CNH válida encontrada no texto.",
                    invalid_risk="medium",
                    invalid_reason="CNH inválida."
                )
            )

            issues.extend(
                self._build_issues(
                    issue_type="RG",
                    matches=rg_matches,
                    validator=is_valid_rg,
                    valid_risk="medium",
                    valid_reason="RG encontrado no texto.",
                    invalid_risk="low",
                    invalid_reason="RG inválido."
                )
            )
        return ScanResult(issues)
