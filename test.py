import json

from dpokitpy import Guard
from dpokitpy.validators.br.rg import find_rgs
from dpokitpy.validators.br.rg_sp import is_valid_sp_rg_format
from dpokitpy.validators.br.cnpj import find_cnpjs, is_valid_cnpj

guard = Guard()

# ==================================================
# TEXTO CONTÍNUO DE TESTE
# Casos validados até agora:
# - CPF válido e inválido
# - CNPJ numérico bruto
# - CNPJ alfanumérico mascarado e bruto
# - Email
# - Telefone BR válido
# - RG SP e RG genérico
# - Máscara / hash / scanner
# ==================================================

texto = """
Cliente informou CPF 529.982.247-25 e também CPF antigo 123.456.789-00.

Empresa A possui CNPJ 11.222.333/0001-80.
Empresa B informou CNPJ bruto 11222333000180.

Novo cadastro alfanumérico:
A1.BC2.34D/56EF-20
A1BC234D56EF20
AB.123.CDE/0001-99
AB123CDE000199

Contato principal: teste@gmail.com
Telefone comercial: (11) 91234-5678

Documentos apresentados:
RG SP válido 12.345.678-9
RG SP formato alternativo 123456789
RG antigo 12.345.678-X
Identidade geral 987654321
Documento complementar 12345678X
"""

print("=" * 70)
print("TEXTO ANALISADO")
print("=" * 70)
print(texto)

# ==================================================
# SAFE
# ==================================================
print("\n=== is_safe ===")
print(guard.is_safe(texto))

# ==================================================
# FIND
# ==================================================
print("\n=== find ===")
result = guard.find(texto)

try:
    print(json.dumps([x.to_dict() for x in result], indent=2, ensure_ascii=False))
except:
    print(result)

# ==================================================
# VALIDATE
# ==================================================
print("\n=== validate ===")
result = guard.validate(texto)

try:
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
except:
    print(result)

# ==================================================
# MASK
# ==================================================
print("\n=== mask ===")
print(guard.mask(texto))

# ==================================================
# HASH
# ==================================================
print("\n=== hash ===")
print("Hash Original :", guard.hash_original(texto))
print("Hash Mascarado:", guard.hash_masked(texto))

# ==================================================
# RG
# ==================================================
print("\n=== RG ===")
print("RGs encontrados:", find_rgs(texto))
print("SP 123456789 :", is_valid_sp_rg_format("123456789"))
print("SP 12345678X:", is_valid_sp_rg_format("12345678X"))

# ==================================================
# CNPJ
# ==================================================
print("\n=== CNPJ ===")
print(find_cnpjs(texto))
print("A1.BC2.34D/56EF-20:", is_valid_cnpj("A1.BC2.34D/56EF-20"))
print("A1BC234D56EF20   :", is_valid_cnpj("A1BC234D56EF20"))
print("11.222.333/0001-80:", is_valid_cnpj("11.222.333/0001-80"))

# ==================================================
# SAFE FINAL
# ==================================================
print("\n=== is_safe (final) ===")
print(guard.is_safe(texto))
