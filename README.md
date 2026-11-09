# 🛒 Pipeline de Dados E-Commerce Tech Store (Python + SQL)

Projeto final desenvolvido para a plataforma **Emprega Dados** — *Trilha de Engenharia de Dados Júnior*.

Este repositório implementa um pipeline completo de engenharia de dados ponta a ponta dividido em **três camadas arquiteturais** (`raw`, `refined` e `marts`), utilizando **Python**, **SQL (SQLite)**, **pytest** e uma interface interativa de terminal (CLI).

---

## 🎯 1. Fonte dos Dados

Os dados simulam o ecossistema transacional de uma loja virtual brasileira de eletrônicos e acessórios de informática (*Tech Store*), estruturados em arquivos CSV na pasta [`data/raw/`](data/raw/):

* **Origem:** Dados sintéticos estruturados baseados no domínio do varejo eletrônico brasileiro.
* **Licença:** **MIT / Public Domain (CC0)** — Permitido uso e distribuição livre para repositórios públicos.
* **Integridade da Camada Bruta:** Conforme premissa da engenharia de dados, **nenhum arquivo dentro de `data/raw/` é alterado manualmente**.

---

## 📐 2. O que é uma linha de cada tabela (Granularidade)

| Tabela | O que representa cada linha (Granularidade) | Chave Primária (PK) | Chaves Estrangeiras (FK) |
|---|---|---|---|
| **`clientes`** | Um cliente único cadastrado na plataforma, com seus dados cadastrais e localização. | `id_cliente` | - |
| **`produtos`** | Um produto específico do catálogo da loja, sua categoria, preço de venda e custo. | `id_produto` | - |
| **`pedidos`** | Uma transação/carrinho fechado por um cliente, com data, status e meio de pagamento. | `id_pedido` | `id_cliente` -> `clientes` |
| **`itens_pedido`** | Uma linha de item contido dentro de um pedido, indicando qual produto foi comprado e sua quantidade. | `id_item` | `id_pedido` -> `pedidos`, `id_produto` -> `produtos` |

---

## 🏗️ 3. As Três Camadas do Pipeline

```text
       [ data/raw/*.csv ]
               │
               ▼  (Ingestão sem alterações)
┌──────────────────────────────────────┐
│  1. CAMADA RAW (raw_*)              │  -> Dados brutos intocados (persistidos no SQLite)
└──────────────────────────────────────┘
               │
               ▼  (src/transform.py: strip, tipagem, cálculos derivados, FKs)
┌──────────────────────────────────────┐
│  2. CAMADA REFINED (refined_*)       │  -> Tabelas normalizadas, limpas e com integridade
└──────────────────────────────────────┘
               │
               ▼  (sql/marts/*.sql: regras de negócio e agregações)
┌──────────────────────────────────────┐
│  3. CAMADA MARTS (marts_*)           │  -> Indicadores analíticos para tomada de decisão
└──────────────────────────────────────┘
```

### Indicadores e Modelos Analíticos Gerados:
Cada indicador de negócio possui um arquivo `.sql` exclusivo e documentado na pasta [`sql/marts/`](sql/marts/):

1. **[`faturamento_por_categoria.sql`](sql/marts/faturamento_por_categoria.sql):**
   * *Métricas:* Itens vendidos, Receita bruta, Custo total, Lucro bruto e Margem percentual.
   * *Decisão:* Exclui pedidos cancelados (`status != 'cancelado'`), garantindo precisão financeira.
2. **[`produtos_mais_vendidos.sql`](sql/marts/produtos_mais_vendidos.sql):**
   * *Métricas:* Volume de unidades vendidas, contagem de pedidos distintos e faturamento total por produto.
3. **[`faturamento_por_cliente.sql`](sql/marts/faturamento_por_cliente.sql):**
   * *Métricas:* Total de pedidos por cliente, valor acumulado gasto (LTV inicial) e ticket médio individual.
4. **[`metricas_mensais_ticket_medio.sql`](sql/marts/metricas_mensais_ticket_medio.sql):**
   * *Métricas:* Evolução mensal (`YYYY-MM`) de pedidos, compradores únicos, faturamento e ticket médio por pedido.

---

## 🚀 4. Como Executar do Zero

### Pré-requisitos
* **Python 3.10+**
* **Git**

### Passo a Passo

```bash
# 1. Clone o repositório
git clone <URL_DO_SEU_REPOSITORIO>
cd <PASTA_DO_REPOSITORIO>

# 2. (Opcional, porém recomendado) Crie e ative um ambiente virtual
python -m venv .venv

# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
# No Linux / macOS:
# source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute os testes unitários automatizados
pytest -v

# 5. Execute o pipeline completo ou abra o menu interativo
# Opção A: Executar o pipeline ponta a ponta via comando
python src/main.py --run-pipeline

# Opção B: Abrir o menu interativo no terminal
python src/main.py
```

---

## ✅ 5. Testes Unitários (`pytest`)

Os testes automatizados foram construídos seguindo estritamente a exigência do curso: **rodam com dados mockados em memória (`sqlite3.connect(':memory:')`), sem abrir e sem depender do arquivo de banco de dados real do projeto**.

Comando para rodar:
```bash
pytest -v
```

Cenários cobertos:
* **Limpeza e Padronização:** Remoção de espaços espúrios, formatação ISO de datas e e-mails em minúsculas.
* **Cálculo Derivado:** Validação matemática de subtotais de itens (`quantidade * preco_unitario`).
* **Regra de Negócio de Marts:** Teste comprovando que pedidos com status `'cancelado'` são devidamente desconsiderados do faturamento na camada de indicadores.

---

## 🤖 6. Auditoria da Inteligência Artificial (Onde a IA errou e como conferimos)

> *"Um projeto em que a IA não errou nenhuma vez é um projeto em que ninguém conferiu."*

Durante o desenvolvimento deste pipeline em conjunto com o assistente de IA, identificamos e corrigimos dois erros conceituais críticos através de auditoria e contagem de linhas:

1. **Suposição de Faturamento Total sem Filtro de Cancelamentos:**
   * **O erro da IA:** Na primeira proposta das consultas SQL da camada `marts`, a IA realizou um `SUM(subtotal)` direto relacionando `itens_pedido` com `pedidos`, sem filtrar a coluna `status`.
   * **Como descobrimos:** Ao auditar a contagem de linhas antes e depois da transformação, notamos que a tabela `raw_pedidos` possuía 15 pedidos, sendo 2 com status `'cancelado'`. Somando a receita total sugerida pela IA, o valor incluía os R\$ 890,00 da Cadeira Gamer do pedido cancelado 1004.
   * **Correção aplicada:** Inserção obrigatória da cláusula `WHERE ped.status != 'cancelado'` em todas as consultas da camada de indicadores e criação de um teste unitário com pytest para garantir que essa regra nunca seja violada.

2. **Incompatibilidade de Codificação no Terminal Windows (UnicodeEncodeError):**
   * **O erro da IA:** A IA inseriu ícones e emojis (`🚀`, `✔`) diretamente nos comandos `print()` do terminal da CLI.
   * **Como descobrimos:** Ao testar a execução no ambiente Windows (PowerShell/CMD sob encoding padrão `charmap / cp1252`), o script quebrou imediatamente com `UnicodeEncodeError`.
   * **Correção aplicada:** Substituição dos emojis por marcadores ASCII seguros e universais (`[OK]`, `>>>`, `[!]`) e adição de `sys.stdout.reconfigure(encoding="utf-8")`, garantindo portabilidade cross-platform.

---

## 👤 Autor

* **Aluno:** Alex
* **Curso:** Trilha de Engenharia de Dados Júnior — Emprega Dados
