import re


class Masker:

    def mask(self, text: str, issues: list):
        masked_text = text

        clean_text = text.strip()

        # fallback seguro para RG isolado
        if re.fullmatch(r"\d{9}|\d{8}[Xx]", clean_text):
            return self._mask_rg(clean_text)

        for issue in issues:
            if issue.type == "CPF":
                masked_value = self._mask_cpf(issue.value)
                masked_text = masked_text.replace(issue.value, masked_value)

            elif issue.type == "CNPJ":
                masked_value = self._mask_cnpj(issue.value)
                masked_text = masked_text.replace(issue.value, masked_value)

            elif issue.type == "EMAIL":
                masked_value = self._mask_email(issue.value)
                masked_text = masked_text.replace(issue.value, masked_value)

            elif issue.type == "PHONE":
                masked_value = self._mask_phone(issue.value)
                masked_text = masked_text.replace(issue.value, masked_value)

            elif issue.type == "RG":
                masked_value = self._mask_rg(issue.value)
                masked_text = masked_text.replace(issue.value, masked_value)

        return masked_text.strip()

    def _mask_cpf(self, cpf: str) -> str:
        digits = ''.join(filter(str.isdigit, cpf))
        return "***.***.***-" + digits[-2:]

    def _mask_email(self, email: str) -> str:
        name, domain = email.split("@")
        return name[0] + "***@" + domain

    def _mask_phone(self, phone: str) -> str:
        digits = ''.join(filter(str.isdigit, phone))
        return "(**)" + " *****-" + digits[-4:]

    def _mask_rg(self, rg: str) -> str:
        clean = rg.strip()

        # formato mascarado tipo SP (12.345.678-9)
        if "." in clean and "-" in clean:
            return "**.***.***-*"

        # remove não numérico (mantém X)
        clean_digits = ''.join(filter(lambda x: x.isdigit() or x.upper() == 'X', clean))

        if len(clean_digits) <= 2:
            return "*" * len(clean_digits)

        # mantém últimos 2 dígitos/letra
        return "*" * (len(clean_digits) - 2) + clean_digits[-2:]

    def _mask_cnpj(self, cnpj: str) -> str:
        digits = ''.join(filter(str.isalnum, cnpj.upper()))

        if len(digits) < 2:
            return "*" * len(digits)

        # mantém só últimos 2
        hidden = "*" * (len(digits) - 2)
        tail = digits[-2:]

        raw = hidden + tail

        # se 14 chars, devolve formato clássico
        if len(raw) == 14:
            return f"{raw[:2]}.{raw[2:5]}.{raw[5:8]}/{raw[8:12]}-{raw[12:]}"

        return raw
