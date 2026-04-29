# 🚀 S2MOdataPy - OData V4 Client Library

**S2MOdataPy** (Simple 2 Master OData Python) é uma biblioteca leve, intuitiva e extensível projetada para simplificar a interação com serviços **OData V4**, focando em robustez, facilidade de depuração e suporte multi-formato.

---

## 👤 Autor

**Christopher N. S. M. Mauricio**

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ChristopherNicolasSMM/S2MOdataPy)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/christophernicolassmm/)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:christopher.nicolas.mauricio@gmail.com)

---

## ✨ Features

| Característica | Descrição |
|----------------|------------|
| 🚀 **Query Builder Fluente** | Encadeamento intuitivo de métodos (`.filter().select().top()`) |
| 🐛 **Modo Debug Integrado** | Visualização completa de URLs, headers e payloads em tempo real |
| 📦 **Suporte Multi-Formato** | JSON (padrão) e XML para compatibilidade com sistemas legados |
| 🔄 **Paginação Automática** | Controle fácil com `$top`, `$skip` e `$count` |
| 🎯 **Type Hints** | Suporte completo a type hints para melhor produtividade |
| 🔍 **Filtros Avançados** | Suporte a `eq`, `gt`, `lt`, `contains`, `and`, `or` |
| 📊 **Exportação** | Integração futura com Pandas DataFrame |
| ⚡ **Leve e Rápida** | Sem dependências desnecessárias (apenas `requests`) |

---

## 📦 Instalação

### Via pip (futuro)
```bash
pip install s2modatapy
```

### Instalação local (desenvolvimento)
```bash
# Clone o repositório
git clone https://github.com/ChristopherNicolasSMM/S2MOdataPy/S2MOdataPy.git
cd S2MOdataPy

# Crie e ative o ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instale a biblioteca e dependências
pip install -e .
pip install -r requirements.txt
```

---

## 🚀 Quick Start

### Exemplo 1: Consulta básica
```python
from s2modatapy import S2MClient

# Inicializa o cliente
client = S2MClient(
    base_url="https://services.odata.org/V4/Northwind/Northwind.svc/",
    debug=True,  # Ativa debug para ver os detalhes da requisição
    response_format='json'
)

# Consulta fluente
result = client.entity("Customers") \
    .select("CustomerID", "CompanyName", "Country") \
    .filter("Country eq 'Brazil'") \
    .orderby("CompanyName", "asc") \
    .top(5) \
    .get()

# Exibe os resultados
for customer in result['value']:
    print(f"{customer['CustomerID']}: {customer['CompanyName']}")
```

### Exemplo 2: Filtros complexos
```python
# Produtos com preço > 50 e em estoque
result = client.entity("Products") \
    .select("ProductName", "UnitPrice", "UnitsInStock") \
    .filter("UnitPrice gt 50 and UnitsInStock gt 0") \
    .orderby("UnitPrice", "desc") \
    .get()
```

### Exemplo 3: Paginação
```python
# Página 2 (itens 11-20)
result = client.entity("Orders") \
    .select("OrderID", "OrderDate") \
    .orderby("OrderDate", "desc") \
    .skip(10) \
    .top(10) \
    .get()
```

### Exemplo 4: Expandindo relacionamentos
```python
# Pedidos com dados do cliente
result = client.entity("Orders") \
    .select("OrderID", "OrderDate") \
    .expand("Customer") \
    .filter("OrderDate ge 1998-01-01") \
    .top(5) \
    .get()

for order in result['value']:
    print(f"Pedido {order['OrderID']} - {order['Customer']['CompanyName']}")
```

### Exemplo 5: Contagem total
```python
# Apenas contar registros (sem trazer dados)
total = client.entity("Orders") \
    .filter("OrderDate ge 1998-01-01") \
    .count_only()

print(f"Total de pedidos: {total}")
```

---

## 📚 API Reference

### Cliente Principal

| Método | Parâmetros | Retorno | Descrição |
|--------|-----------|---------|-----------|
| `S2MClient()` | `base_url`, `debug`, `response_format` | `S2MClient` | Inicializa o cliente |
| `entity()` | `entity_name: str` | `ODataQueryBuilder` | Inicia uma consulta |

### Query Builder

| Método | Parâmetros | Descrição |
|--------|-----------|-----------|
| `select()` | `*fields: str` | Seleciona campos específicos |
| `filter()` | `condition: str` | Aplica filtro OData |
| `orderby()` | `field: str, direction: str` | Ordena resultados |
| `top()` | `n: int` | Limita número de resultados |
| `skip()` | `n: int` | Pula N resultados |
| `expand()` | `*entities: str` | Expande relacionamentos |
| `count()` | `enabled: bool` | Inclui contagem total |
| `get()` | - | Executa a consulta |
| `first()` | - | Retorna apenas o primeiro |
| `count_only()` | - | Retorna apenas a contagem |

---

## 🐛 Modo Debug

O modo debug é essencial para desenvolvimento. Quando ativado, mostra:

```python
client = S2MClient(base_url="...", debug=True)
```

**Saída exemplo:**
```
======================================================================
🔍 [S2MOdataPy DEBUG] 2024-01-15 14:30:25.123
======================================================================
📡 Método: GET
📍 URL: https://services.odata.org/V4/Northwind/Northwind.svc/Customers

📊 Parâmetros Query String:
   $filter = Country eq 'Brazil'
   $select = CustomerID,CompanyName,Country
   $orderby = CompanyName asc

📥 Resposta Recebida:
   Status: 200 OK
   Tempo: 0.234 segundos
   Registros retornados: 9
======================================================================
```

---

## 🧪 Testes

Execute os testes unitários:

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements.txt

# Rodar testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=s2modatapy --cov-report=html
```

---

## 📁 Estrutura do Projeto

```
S2MOdataPy/
├── s2modatapy/
│   ├── __init__.py          # Inicialização da biblioteca
│   ├── client.py            # Cliente principal
│   ├── query_builder.py     # Query builder fluente
│   ├── debug.py             # Modo debug
│   ├── exceptions.py        # Exceções customizadas
│   └── parsers/             # Parsers (JSON/XML)
├── tests/                   # Testes unitários
├── examples/                # Exemplos de uso
├── docs/                    # Documentação
├── pyproject.toml           # Configuração do projeto
├── requirements.txt         # Dependências
├── LICENSE                  # Licença (MIT with Attribution)
└── README.md                # Este arquivo
```

---

## 🤝 Como Contribuir

1. Faça um fork do projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

**Créditos obrigatórios em qualquer contribuição:**
> "Contribuição para S2MOdataPy por Christopher N. S. M. Mauricio"

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License with Attribution** - veja o arquivo [LICENSE](LICENSE) para detalhes.

**Atribuição obrigatória:**
```
Christopher N. S. M. Mauricio - S2MOdataPy
https://github.com/ChristopherNicolasSMM/S2MOdataPy/S2MOdataPy
```

---

## 📞 Suporte e Contato

- 🐛 **Reportar bugs**: [Issues GitHub](https://github.com/ChristopherNicolasSMM/S2MOdataPy/S2MOdataPy/issues)
- 💡 **Sugestões**: [Discussions GitHub](https://github.com/ChristopherNicolasSMM/S2MOdataPy/S2MOdataPy/discussions)
- 📧 **Email direto**: christopher.nicolas.mauricio@gmail.com

---

## 🌟 Roadmap

| Versão | Features |
|--------|----------|
| **v0.1** | ✅ Core, Query Builder, Debug, JSON support |
| **v0.2** | 🔄 XML Parser, Autenticação (Basic/Token) |
| **v0.3** | 📊 Batch Requests, Exportação Pandas |
| **v0.4** | 🚀 CLI interativo, Cache automático |

---

## 🙏 Agradecimentos

- Microsoft pelo padrão OData
- Comunidade Python por bibliotecas incríveis
- Você por utilizar S2MOdataPy!

---

**Made with ❤️ by Christopher N. S. M. Mauricio**

[⬆ Voltar ao topo](#-s2modatapy---odata-v4-client-library)
