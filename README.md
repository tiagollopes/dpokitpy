# dpokitpy

> ⚠️ **Projeto piloto em desenvolvimento (POC)**
> Esta biblioteca está em fase inicial e pode sofrer mudanças frequentes.

Biblioteca Python para detecção, validação, mascaramento e auditoria de dados sensíveis (PII), com foco inicial em regras brasileiras (LGPD).

---

##  O que é o dpokitpy?

O `dpokitpy` analisa textos e identifica dados sensíveis como:

- CPF
- CNPJ
- Email
- Telefone

E aplica automaticamente:

- ✔ validação dos dados
- ✔ classificação de risco
- ✔ aplicação de políticas (LGPD)
- ✔ mascaramento de dados
- ✔ geração de auditoria
- ✔ API simples para integração

---

##  Arquitetura (fluxo)

Guard.validate(text)
    ↓
Scanner.scan(text)
    ↓
Validators (CPF, CNPJ, EMAIL, PHONE)
    ↓
Policy (LGPD BR)
    ↓
ScanResult (issues)
    ↓
Masker (masked_text)
    ↓
AuditLogger (audit_record)
    ↓
Resultado final

# 📦 Estrutura do projeto

dpokitpy/

<pre>
├── test.py
└── dpokitpy/
    ├── guard.py
    ├── scanner.py
    ├── models.py
    ├── masker.py
    ├── audit_logger.py
    ├── validators/
    │   └── br/
    │       ├── cpf.py
    │       ├── cnpj.py
    │       ├── email.py
    │       └── phone.py
    └── policies/
        └── br/
            └── lgpd.py
</pre>

# ⚙️ Como usar
<pre>from dpokitpy import Guard

guard = Guard()

text = "CPF: 529.982.247-25 | Email: teste@gmail.com"

print(guard.is_safe(text))
print(guard.find(text))
print(guard.mask(text))
print(guard.validate(text))

</pre>

# Exemplo de saída

<pre>
{
    "is_safe": False,
    "total_issues": 2,
    "issues": [
        {
            "type": "CPF",
            "value": "529.982.247-25",
            "valid": True,
            "risk": "high",
            "action": "block"
        },
        {
            "type": "EMAIL",
            "value": "teste@gmail.com",
            "valid": True,
            "risk": "medium",
            "action": "warn"
        }
    ],
    "masked_text": "CPF: ***.***.***-25 | Email: t***@gmail.com"
}
</pre>

# 📊 Regras atuais

* **Detecção
- Tipo	Regra
- CPF	exige CPF:
- CNPJ	exige CNPJ:
- PHONE	exige Telefone:
- EMAIL	padrão livre

* **Risco

- CPF válido → high
- CNPJ válido → high
- EMAIL válido → medium
- PHONE válido → medium
- Policy (LGPD BR)
- CPF válido → block
- CNPJ válido → block
- EMAIL válido → warn
- PHONE válido → warn
- inválidos → ignore

# Componentes principais

- Guard → fachada da API
- Scanner → engine de análise
- Validators → validação por tipo
- Policy → regras de negócio
- Masker → mascaramento
- AuditLogger → auditoria

# Estado atual

 - arquitetura modular
 - validação de CPF/CNPJ
 - detecção de email/telefone
 - classificação de risco
 - mascaramento
 - auditoria com hash
 - API funcional

 # 🔜 Próximos passos

 - melhorar políticas (review, report)
- otimizar performance
- adicionar categoria (PII / sensitive)
- suporte a outros países
- empacotamento para PyPI

# Status

Projeto experimental voltado para estudo de arquitetura de bibliotecas Python focadas em segurança e compliance de dados.

 # Autor

Tiago Lopes - Santos/SP (BRASIL)
https://github.com/tiagollopes
