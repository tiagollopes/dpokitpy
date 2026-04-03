class Masker:

    def mask(self, text: str, issues: list):
        masked_text = text

        for issue in issues:
            if issue.valid and issue.type == "CPF":
                masked_value = self._mask_cpf(issue.value)
                masked_text = masked_text.replace(issue.value, masked_value)

            elif issue.valid and issue.type == "EMAIL":
                masked_value = self._mask_email(issue.value)
                masked_text = masked_text.replace(issue.value, masked_value)

            elif issue.valid and issue.type == "PHONE":
                masked_value = self._mask_phone(issue.value)
                masked_text = masked_text.replace(issue.value, masked_value)

        return masked_text

    def _mask_cpf(self, cpf: str) -> str:
        digits = ''.join(filter(str.isdigit, cpf))
        return "***.***.***-" + digits[-2:]

    def _mask_email(self, email: str) -> str:
        name, domain = email.split("@")
        return name[0] + "***@" + domain

    def _mask_phone(self, phone: str) -> str:
        digits = ''.join(filter(str.isdigit, phone))
        return "(**)" + " *****-" + digits[-4:]
