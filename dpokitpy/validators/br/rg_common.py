import re
from typing import Optional

POSITIVE_CONTEXT_WORDS = (
    "rg",
    "registro geral",
    "identidade",
    "doc identidade",
    "documento de identidade",
    "carteira de identidade",
    "numero do rg",
    "número do rg",
    "meu rg",
    "rg es",
    "rg mg",
    "rg rj",
    "rg sp",
    "rg ssp/sp",
    "ssp",
    "iirgd",
)

NEGATIVE_CONTEXT_WORDS = (
    "protocolo",
    "pedido",
    "codigo",
    "código",
    "token",
    "identificador",
    "id ",
    " id ",
    "id:",
    "id-",
    "matricula",
    "matrícula",
    "lote",
    "ref",
    "referência",
    "referencia",
    "boleto",
    "pix",
    "nf",
    "nfe",
    "senha",
    "cpf",
    "cnpj",
    "cep",
    "telefone",
    "celular",
)

UF_CODES = {
    "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA",
    "MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN",
    "RS","RO","RR","SC","SP","SE","TO"
}


def normalize_rg(rg: str) -> str:
# Mantém letras e números para não perder o 'X' final ou a sigla da UF
    return re.sub(r"[^0-9A-Za-z]", "", rg).upper()


def digits_only(value: str) -> str:
    return re.sub(r"[^0-9]", "", value)


def has_positive_context(context: str) -> bool:
    if not context:
        return False
    return any(w in context.lower() for w in POSITIVE_CONTEXT_WORDS)


def has_negative_context(context: str) -> bool:
    if not context:
        return False
    return any(w in context.lower() for w in NEGATIVE_CONTEXT_WORDS)


def has_strong_rg_context(context: str) -> bool:
    if not context:
        return False

    strong_terms = (
        "meu rg",
        "numero do rg",
        "número do rg",
        "documento de identidade",
        "carteira de identidade",
        "registro geral",
        "rg ssp/sp",
        "rg sp",
        "rg rj",
        "rg mg",
        "rg es",
        "rg ",
        "rg:",
    )

    context_lc = context.lower()
    return any(t in context_lc for t in strong_terms)


def is_repeated_sequence(value: str) -> bool:
    return len(value) > 0 and len(set(value)) == 1


def is_obviously_invalid_rg(rg: str) -> bool:
    rg_norm = normalize_rg(rg)
    only_digits = digits_only(rg_norm)

    if not rg_norm:
        return True

    if rg_norm in {"MG", "ES", "SP", "RJ", "RGM"}:
        return True

    if only_digits and len(only_digits) >= 5 and is_repeated_sequence(only_digits):
        return True

    return False


def extract_uf_from_rg(rg: str) -> Optional[str]:
    rg_norm = normalize_rg(rg)

    if len(rg_norm) >= 2 and rg_norm[-2:] in UF_CODES:
        return rg_norm[-2:]

    if len(rg_norm) >= 2 and rg_norm[:2] in UF_CODES:
        return rg_norm[:2]

    if rg_norm.startswith("RGM"):
        return "MG"

    return None


def extract_uf_from_context(context: str) -> Optional[str]:
    if not context: return None
    context_up = context.upper()

    patterns = [
        r"\b(?:SSP|RG|IDENTIDADE|DOCUMENTO)[\s\/\-\:]+([A-Z]{2})\b",
        r"\b([A-Z]{2})[\s\:]+\d{5,}", # Ex: RS: 10947191
    ]

    for p in patterns:
        m = re.search(p, context_up)
        if m:
            uf = m.group(1)
            if uf in UF_CODES: return uf
    return None

def detect_rg_state(rg: str, context: str = "") -> Optional[str]:
    return extract_uf_from_rg(rg) or extract_uf_from_context(context)


def split_core_and_uf(rg: str, uf: Optional[str] = None):
    rg_norm = normalize_rg(rg)

    detected = uf
    if not detected and len(rg_norm) >= 2 and rg_norm[-2:] in UF_CODES:
        detected = rg_norm[-2:]

    if rg_norm.startswith("RGM"):
        return rg_norm[3:], "MG"

    if detected and rg_norm.endswith(detected):
        return rg_norm[:-2], detected

    return rg_norm, detected
