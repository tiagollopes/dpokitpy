import json
from dpokitpy import Guard
from dpokitpy.validators.br.rg import find_rgs
from dpokitpy.validators.br.rg_sp import is_valid_sp_rg_format

guard = Guard()

# ===============================
# TEXTO DE TESTE (COMPLETO)
# ===============================
texto = """
12.345.678-X
123.456.789-00
CPF: 529.982.247-25
Email: teste@gmail.com
Telefone: (11) 91234-5678

RG SP válido: RG SP 12.345.678-9
RG SP inválido: RG SP 123456789

RG genérico: Identidade 987654321
Documento de identidade 12345678X
"""

print("===================================")
print("TEXTO ANALISADO:")
print(texto)
print("===================================")


# ===============================
# is_safe
# ===============================
print("\n=== is_safe ===")
print(guard.is_safe(texto))


# ===============================
# find (somente ocorrências)
# ===============================
print("\n=== find ===")
find_result = guard.find(texto)

try:
    print(json.dumps([item.to_dict() for item in find_result], indent=2, ensure_ascii=False))
except AttributeError:
    print(find_result)


# ===============================
# validate (resultado completo)
# ===============================
print("\n=== validate ===")
validate_result = guard.validate(texto)

try:
    print(json.dumps(validate_result.to_dict(), indent=2, ensure_ascii=False))
except AttributeError:
    print(validate_result)


# ===============================
# mask
# ===============================
print("\n=== mask ===")
print(guard.mask(texto))


# ===============================
# hash
# ===============================
print("\n=== hash ===")
print(f"Hash Original:  {guard.hash_original(texto)}")
print(f"Hash Mascarado: {guard.hash_masked(texto)}")
print("RGs encontrados:")
print(find_rgs(texto))
print("=== is_safe ===")
print(guard.is_safe(texto))
print("FORMATO 123456789:", is_valid_sp_rg_format("123456789"))
print("FORMATO 12345678X:", is_valid_sp_rg_format("12345678X"))
