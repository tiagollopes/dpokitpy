# dpokitpy

Biblioteca Python para **detecção, validação, mascaramento e auditoria de dados sensíveis (PII)**, com foco inicial em **regras brasileiras** e aderência a cenários de **LGPD, segurança, compliance e apoio a funções de DPO (Data Protection Officer)**.

> Projeto experimental, porém já funcional, modular e validado por benchmarks automatizados.
> 100% offline. Nenhum dado é enviado ou armazenado.


## Visão geral

O `dpokitpy` foi criado para analisar textos livres e identificar dados sensíveis, validar sua plausibilidade, aplicar classificação de risco, definir ação recomendada, mascarar os dados encontrados e gerar informações de auditoria.

Atualmente, a biblioteca já oferece um fluxo completo de:

- detecção
- validação
- classificação de risco
- aplicação de ação
- mascaramento
- geração de hash
- auditoria
- benchmark automatizado

## Objetivos do projeto

O projeto foi pensado para cenários como:

- proteção de dados sensíveis em textos
- sanitização de logs
- análise de entradas de usuário
- auditoria de conteúdo textual
- validação de dados antes de persistência
- apoio a pipelines de governança e compliance
- futura integração com filtros de saída de IA / LLM

## 🛡️ Privacidade e Segurança

O `dpokitpy` foi projetado com foco em **privacidade e proteção de dados sensíveis**.

### Garantias importantes

- ❌ Não envia dados para APIs externas
- ❌ Não realiza chamadas de rede
- ❌ Não armazena textos analisados
- ❌ Não persiste dados sensíveis em disco
- ❌ Não gera logs com conteúdo original

- ✅ Todo processamento ocorre localmente (offline)
- ✅ Os dados são processados apenas em memória
- ✅ Nenhuma informação sensível é retida após a execução

### Auditoria segura

A auditoria gerada pelo sistema **não expõe o conteúdo original**.

Em vez disso, utiliza:

- Hash SHA-256 do texto original
- Hash SHA-256 do texto mascarado

Isso permite:

- rastreabilidade
- comparação de resultados
- auditoria segura

sem necessidade de armazenar dados sensíveis.

### Importante

O uso da biblioteca é seguro para:

- análise de textos locais
- sanitização de logs
- validação de entrada de dados

desde que o próprio ambiente de execução também siga boas práticas de segurança.

## Tipos suportados

Atualmente o `dpokitpy` suporta:

- CPF
- CNPJ
- EMAIL
- PHONE
- PIS
- CNH
- RG

## RG com validação avançada

O RG foi implementado com arquitetura separada por estado para reduzir conflitos e melhorar precisão.

### Estrutura do RG

- `rg.py` → orquestrador principal
- `rg_rj.py` → regras específicas do RJ
- `rg_es.py` → regras específicas do ES
- `rg_mg.py` → regras específicas de MG
- `rg_sp.py` → validação de SP com dígito verificador
- `rg_outros.py` → fallback genérico para demais casos

### Estratégia

- estados específicos têm prioridade
- RG genérico cai no fallback
- evita colisão entre formatos diferentes
- SP possui validação de dígito verificador
- formatos mascarados e pontuados são tratados corretamente

## Fluxo principal

Fluxo da chamada principal:

<pre>
Guard.validate(text)
    ↓
Scanner.scan(text)
    ↓
Validators por tipo
    ↓
Policy / classificação
    ↓
Masker
    ↓
AuditLogger
    ↓
Resultado final

Arquitetura do projeto
</pre>

<pre>
dpokitpy/
├── benchmark/
│   ├── bm_cnh.py
│   ├── bm_cnpj.py
│   ├── bm_cpf.py
│   ├── bm_email.py
│   ├── bm_phone.py
│   ├── bm_pis.py
│   ├── bm_rg.py
│   ├── bm_rg_es.py
│   ├── bm_rg_mg.py
│   ├── bm_rg_outros.py
│   ├── bm_rg_rj.py
│   ├── bm_rg_sp.py
│   └── runner.py
├── dpokitpy/
│   ├── audit_logger.py
│   ├── guard.py
│   ├── masker.py
│   ├── models.py
│   ├── scanner.py
│   ├── policies/
│   │   └── br/
│   └── validators/
│       └── br/
├── README.md
└── test.py
</pre>

# Componentes principais
- Guard

Interface principal da biblioteca. Expõe os métodos públicos para consumo.

- Scanner

Responsável por detectar padrões e acionar validadores.

- Validators

Módulos específicos para validação por tipo de dado.

- Masker

Responsável por mascarar os dados sensíveis encontrados.

- AuditLogger

Gera informações de auditoria, incluindo hash do texto original e mascarado.

- Policies

Centraliza regras de risco e ação recomendada.

- API principal

Uso típico:

<pre>
from dpokitpy import Guard

guard = Guard()

text = """
CPF: 529.982.247-25
Email: teste@gmail.com
Telefone: (11) 91234-5678

RG SP válido: RG SP 12.345.678-9
RG genérico: Identidade 987654321
"""

print(guard.is_safe(text))
print(guard.find(text))
print(guard.mask(text))

result = guard.validate(text)
print(result)

print("Hash Original:", guard.hash_original(text))
print("Hash Mascarado:", guard.hash_masked(text))
Métodos disponíveis
guard.is_safe(text)
</pre>

- Retorna True se nenhum dado sensível relevante for encontrado.
<pre>
guard.find(text)
</pre>
- Retorna a lista de ocorrências detectadas.
<pre>
guard.validate(text)
</pre>
- Retorna o resultado completo da análise com issues, texto mascarado e auditoria.
<pre>
guard.mask(text)
</pre>
- Retorna o texto já mascarado.
<pre>
guard.hash_original(text)
</pre>
- Retorna o hash SHA-256 do texto original.
<pre>
guard.hash_masked(text)
</pre>
- Retorna o hash SHA-256 do texto mascarado.

<pre>
Exemplo de saída
{
  "is_safe": false,
  "total_issues": 3,
  "issues": [
    {
      "type": "CPF",
      "value": "529.982.247-25",
      "valid": true,
      "risk": "high",
      "reason": "CPF válido encontrado no texto.",
      "action": "block"
    },
    {
      "type": "EMAIL",
      "value": "teste@gmail.com",
      "valid": true,
      "risk": "medium",
      "reason": "Email encontrado no texto.",
      "action": "warn"
    },
    {
      "type": "RG",
      "value": "12.345.678-9",
      "valid": true,
      "risk": "medium",
      "reason": "RG encontrado no texto.",
      "action": "ignore"
    }
  ],
  "masked_text": "CPF: ***.***.***-25\nEmail: t***@gmail.com\nRG SP válido: RG SP **.***.***-*",
  "audit_record": {
    "timestamp": "2026-04-13T17:00:28.180854",
    "country": "BR",
    "total_issues": 3,
    "original_text_hash": "hash_original_exemplo",
    "masked_text_hash": "hash_mascarado_exemplo"
  }
}
</pre>

# Mascaramento

Exemplos de mascaramento atual:

<pre>
CPF: ***.***.***-25
EMAIL: t***@gmail.com
PHONE: (**) *****-5678
RG SP: **.***.***-*
RG genérico: *******21
</pre>

# Auditoria

A auditoria atual gera:

<pre>
timestamp
country
total_issues
original_text_hash
masked_text_hash
</pre>

Isso permite rastreabilidade básica do conteúdo analisado sem expor diretamente o conteúdo original em logs.

# Benchmark

O projeto possui benchmarks individuais por tipo de dado e benchmarks específicos para RG.

Benchmarks disponíveis

<pre>
bm_cpf.py
bm_cnpj.py
bm_email.py
bm_phone.py
bm_pis.py
bm_cnh.py
Benchmarks de RG
bm_rg_rj.py
bm_rg_es.py
bm_rg_mg.py
bm_rg_sp.py
bm_rg_outros.py
</pre>

# Runner consolidado

O arquivo `runner.py` executa todos os benchmarks e consolida os resultados.

# Resultado atual

Estado atual do projeto:

<pre>
arquitetura modular
fluxo completo funcional
validação por tipo
mascaramento implementado
hash de texto original e mascarado
auditoria funcional
benchmarks automatizados
runner consolidado
precisão global validada nos testes atuais
Resultado consolidado informado
aproximadamente 31.000 amostras
0 erros
100% de precisão global
RG com 100% em:
RJ
ES
MG
SP
OUTROS
Instalação local
git clone https://github.com/tiagollopes/dpokitpy.git
cd dpokitpy
python3 -m venv venv
source venv/bin/activate
</pre>

# Como testar

Rodar o teste principal:

<pre>
python3 test.py
</pre>

Rodar benchmark consolidado:

<pre>
python3 benchmark/runner.py
</pre>

Autor

Tiago Lopes
Santos/SP - Brasil

GitHub: tiagollopes

Repositório: dpokitpy
