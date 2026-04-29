#!/usr/bin/env python3
"""
================================================================================
                    S2MOdataPy - TUTORIAL COMPLETO
================================================================================
Biblioteca: S2MOdataPy (Simple 2 Master OData Python)
Autor: Christopher N. S. M. Mauricio
Versão: 0.1.0
Licença: MIT with Attribution

Este tutorial foi desenvolvido para ensinar conceitos do protocolo OData V4
e como utilizar a biblioteca S2MOdataPy de forma prática.

Nível: Iniciante ao Avançado
Tempo estimado de estudo: 30-45 minutos

Conteúdo:
    1. Introdução ao OData e S2MOdataPy
    2. Configuração Inicial (setup)
    3. Consultas Básicas (SELECT)
    4. Filtros (WHERE)
    5. Ordenação (ORDER BY)
    6. Paginação (TOP/SKIP)
    7. Seleção de Campos (SELECT)
    8. Relacionamentos (JOIN com $expand)
    9. Contagem de Registros (COUNT)
    10. Tratamento de Erros
    11. Performance e Boas Práticas
    12. Exemplos Avançados e Casos Reais
    13. Desafios para você praticar

================================================================================
"""

# ============================================================================
# IMPORTAÇÕES NECESSÁRIAS
# ============================================================================

from s2modatapy import S2MClient
from s2modatapy.exceptions import S2MODataError, S2MODataConnectionError
from datetime import datetime, date
import time
import json

# ============================================================================
# PARTE 1: INTRODUÇÃO AO ODATA E S2MODATAPY
# ============================================================================

print("\n" + "="*80)
print(" PARTE 1: INTRODUÇÃO AO ODATA V4 E S2MODATAPY".center(80))
print("="*80)

print("""
O QUE É ODATA?
--------------
OData (Open Data Protocol) é um padrão para construção de APIs RESTful
que permite consultas poderosas diretamente na URL.

EXEMPLOS DE CONSULTAS ODATA:
---------------------------
• /Customers → Lista todos os clientes
• /Customers?$filter=Country eq 'Brazil' → Apenas clientes do Brasil
• /Customers?$select=Name,Phone → Apenas nome e telefone
• /Orders?$orderby=Date desc → Pedidos ordenados por data decrescente

O QUE SUA BIBLIOTECA S2MODATAPY FAZ?
-----------------------------------
Ela transforma essas URLs complexas em código Python fluente e intuitivo!

SEM S2MOdataPy (requisição manual):
----------------------------------
import requests
response = requests.get(
    "https://api.com/Customers?$filter=Country eq 'Brazil'&$select=Name"
)

COM S2MOdataPy (código limpo e fluente):
----------------------------------------
client.entity("Customers").filter("Country eq 'Brazil'").select("Name").get()
""")

input("\n⏸️  Pressione ENTER para continuar para a PARTE 2...")

# ============================================================================
# PARTE 2: CONFIGURAÇÃO INICIAL
# ============================================================================

print("\n" + "="*80)
print(" PARTE 2: CONFIGURAÇÃO INICIAL - CRIANDO O CLIENTE".center(80))
print("="*80)

print("""
CONFIGURANDO O CLIENTE S2MODATAPY:
--------------------------------
A classe principal é 'S2MClient'. Ela recebe 3 parâmetros importantes:

1. base_url (obrigatório): URL do serviço OData
2. debug (opcional, padrão=False): Ativa logs detalhados para desenvolvimento
3. response_format (opcional, padrão='json'): Formato da resposta ('json' ou 'xml')

EXEMPLO PRÁTICO:
--------------""")

# Criando o cliente com diferentes configurações
print("\n📌 Exemplo 1: Cliente padrão (sem debug)")
client_padrao = S2MClient("https://services.odata.org/V4/Northwind/Northwind.svc/")
print("   ✅ Cliente criado com sucesso!")

print("\n📌 Exemplo 2: Cliente com debug (para desenvolvimento)")
client_debug = S2MClient(
    "https://services.odata.org/V4/Northwind/Northwind.svc/",
    debug=True
)
print("   ✅ Cliente com debug criado (recomendado durante desenvolvimento)")

print("\n📌 Exemplo 3: Cliente para produção (sem debug)")
client_prod = S2MClient(
    "https://services.odata.org/V4/Northwind/Northwind.svc/",
    debug=False,
    response_format='json'
)
print("   ✅ Cliente de produção criado (debug desligado para performance)")

# Vamos usar um cliente base para os próximos exemplos
client = S2MClient(
    "https://services.odata.org/V4/Northwind/Northwind.svc/",
    debug=False  # Desligamos o debug para os exemplos básicos
)

print("\n💡 DICA: O debug mostra a URL exata da requisição, headers, tempo de resposta")
print("   e quantidade de registros retornados. É essencial durante o desenvolvimento!")

input("\n⏸️  Pressione ENTER para continuar para a PARTE 3...")

# ============================================================================
# PARTE 3: CONSULTAS BÁSICAS (EQUIVALENTE AO SELECT SIMPLES)
# ============================================================================

print("\n" + "="*80)
print(" PARTE 3: CONSULTAS BÁSICAS - ENTENDENDO O .get()".center(80))
print("="*80)

print("""
CONSULTANDO DADOS COM .get():
---------------------------
O método .get() é o mais importante - ele executa a consulta e retorna os dados.

SINTAXE BÁSICA:
--------------
resultado = client.entity("NOME_ENTIDADE").get()

O resultado é um dicionário Python com a estrutura:
{
    'value': [...],           # Lista de registros encontrados
    '@odata.context': '...',  # Metadata (ignorar por enquanto)
    '@odata.count': 123       # Total de registros (se solicitado)
}

EXEMPLO PRÁTICO - LISTANDO CLIENTES:
-----------------------------------""")

print("\n📋 Consultando os primeiros 5 clientes da Northwind:")
resultado = client.entity("Customers").top(5).get()

print(f"\n📊 Estrutura da resposta:")
print(f"   - Tipo: {type(resultado)}")
print(f"   - Chaves disponíveis: {list(resultado.keys())}")
print(f"   - Total retornado: {len(resultado['value'])} clientes")

print(f"\n📋 Lista de clientes:")
for i, cliente in enumerate(resultado['value'], 1):
    print(f"   {i:2d}. {cliente['CustomerID']:5s} - {cliente['CompanyName'][:35]:35s} - {cliente['Country']}")

print(f"""
💡 EXPLICAÇÃO:
-----------
• resultado['value'] contém a lista de registros
• Cada registro é um dicionário com os campos da entidade
• Se não especificarmos .top(), o serviço pode retornar muitos registros
• Sempre use .top() em desenvolvimento para evitar sobrecarga!
""")

input("\n⏸️  Pressione ENTER para continuar...")

# ============================================================================
# PARTE 4: FILTROS (EQUIVALENTE AO WHERE DO SQL)
# ============================================================================

print("\n" + "="*80)
print(" PARTE 4: FILTROS - O PODER DO .filter()".center(80))
print("="*80)

print("""
FILTRANDO DADOS COM .filter():
----------------------------
O método .filter() aplica condições para selecionar apenas os registros desejados.

OPERADORES DISPONÍVEIS:
---------------------
• eq  → igual (equal)           ex: "Country eq 'Brazil'"
• ne  → diferente (not equal)   ex: "Country ne 'USA'"
• gt  → maior que (greater than) ex: "UnitPrice gt 50"
• ge  → maior ou igual          ex: "OrderDate ge 2024-01-01"
• lt  → menor que (less than)   ex: "UnitsInStock lt 10"
• le  → menor ou igual          ex: "Price le 100"
• contains → contém substring   ex: "contains(ProductName, 'Coffee')"
• startswith → começa com       ex: "startswith(CompanyName, 'A')"
• endswith → termina com        ex: "endswith(Email, '@gmail.com')"

OPERADORES LÓGICOS:
-----------------
• and → E lógico
• or  → OU lógico

EXEMPLOS PRÁTICOS:
----------------""")

# EXEMPLO 1: Filtro simples (igualdade)
print("\n📌 EXEMPLO 1: Clientes do Brasil (filtro de igualdade)")
print("   Filtro: \"Country eq 'Brazil'\"")
resultado = client.entity("Customers")\
    .filter("Country eq 'Brazil'")\
    .select("CustomerID", "CompanyName", "Country")\
    .get()

print(f"   Total de clientes brasileiros: {len(resultado['value'])}")
for cliente in resultado['value']:
    print(f"   → {cliente['CustomerID']}: {cliente['CompanyName']}")

# EXEMPLO 2: Filtro numérico (maior que)
print("\n📌 EXEMPLO 2: Produtos caros (preço > R$ 50)")
print("   Filtro: \"UnitPrice gt 50\"")
resultado = client.entity("Products")\
    .filter("UnitPrice gt 50")\
    .select("ProductName", "UnitPrice")\
    .orderby("UnitPrice", "desc")\
    .top(5)\
    .get()

print(f"   Top 5 produtos mais caros:")
for produto in resultado['value']:
    print(f"   → {produto['ProductName'][:30]:30s} - US$ {produto['UnitPrice']:.2f}")

# EXEMPLO 3: Filtro com string (contém)
print("\n📌 EXEMPLO 3: Produtos que contém 'Coffee' no nome")
print("   Filtro: \"contains(ProductName, 'Coffee')\"")
resultado = client.entity("Products")\
    .filter("contains(ProductName, 'Coffee')")\
    .select("ProductName", "UnitPrice")\
    .get()

print(f"   Produtos encontrados: {len(resultado['value'])}")
for produto in resultado['value']:
    print(f"   → {produto['ProductName']} - US$ {produto['UnitPrice']:.2f}")

# EXEMPLO 4: Filtro combinado (AND)
print("\n📌 EXEMPLO 4: Produtos caros E em estoque (AND)")
print("   Filtro: \"UnitPrice gt 50 and UnitsInStock gt 0\"")
resultado = client.entity("Products")\
    .filter("UnitPrice gt 50 and UnitsInStock gt 0")\
    .select("ProductName", "UnitPrice", "UnitsInStock")\
    .top(5)\
    .get()

print(f"   Produtos disponíveis (caros e em estoque):")
for produto in resultado['value']:
    print(f"   → {produto['ProductName'][:30]:30s} - US$ {produto['UnitPrice']:.2f} (estoque: {produto['UnitsInStock']})")

# EXEMPLO 5: Filtro com data
print("\n📌 EXEMPLO 5: Pedidos recentes (data maior ou igual)")
print("   Filtro: \"OrderDate ge 1998-05-01\"")
resultado = client.entity("Orders")\
    .filter("OrderDate ge 1998-05-01")\
    .select("OrderID", "OrderDate")\
    .orderby("OrderDate", "asc")\
    .top(3)\
    .get()

print(f"   Primeiros pedidos após Maio/1998:")
for pedido in resultado['value']:
    print(f"   → Pedido {pedido['OrderID']:5d} - Data: {pedido['OrderDate']}")

print("""
⚠️  IMPORTANTE:
-------------
• Strings no filtro DEVEM estar entre aspas SIMPLES: "Country eq 'Brazil'"
• Datas usam formato ISO: "OrderDate ge 2024-01-01"
• Combine condições com 'and' e 'or': "Price gt 50 and Stock gt 0"
• Use parênteses para agrupar: "(Price gt 50 or Price lt 10) and Stock gt 0"
""")

input("\n⏸️  Pressione ENTER para continuar...")

# ============================================================================
# PARTE 5: ORDENAÇÃO (EQUIVALENTE AO ORDER BY)
# ============================================================================

print("\n" + "="*80)
print(" PARTE 5: ORDENAÇÃO - ORGANIZANDO RESULTADOS".center(80))
print("="*80)

print("""
ORDENANDO RESULTADOS COM .orderby():
-----------------------------------
O método .orderby() organiza os resultados em ordem crescente (asc) ou decrescente (desc).

SINTAXE:
-------
.orderby(campo, direcao)

• campo: nome do campo a ser ordenado
• direcao: 'asc' (crescente) ou 'desc' (decrescente)

EXEMPLOS PRÁTICOS:
----------------""")

# EXEMPLO 1: Ordenação crescente (menor para maior)
print("\n📌 EXEMPLO 1: Produtos do mais barato ao mais caro (ascendente)")
print("   Ordenação: .orderby(\"UnitPrice\", \"asc\")")
resultado = client.entity("Products")\
    .select("ProductName", "UnitPrice")\
    .orderby("UnitPrice", "asc")\
    .top(5)\
    .get()

print(f"   Produtos mais baratos:")
for produto in resultado['value']:
    print(f"   → {produto['ProductName'][:30]:30s} - US$ {produto['UnitPrice']:.2f}")

# EXEMPLO 2: Ordenação decrescente (maior para menor)
print("\n📌 EXEMPLO 2: Produtos do mais caro ao mais barato (descendente)")
print("   Ordenação: .orderby(\"UnitPrice\", \"desc\")")
resultado = client.entity("Products")\
    .select("ProductName", "UnitPrice")\
    .orderby("UnitPrice", "desc")\
    .top(5)\
    .get()

print(f"   Produtos mais caros:")
for produto in resultado['value']:
    print(f"   → {produto['ProductName'][:30]:30s} - US$ {produto['UnitPrice']:.2f}")

# EXEMPLO 3: Ordenação alfabética
print("\n📌 EXEMPLO 3: Clientes ordenados por nome (alfabético)")
print("   Ordenação: .orderby(\"CompanyName\", \"asc\")")
resultado = client.entity("Customers")\
    .select("CustomerID", "CompanyName")\
    .filter("Country eq 'Brazil'")\
    .orderby("CompanyName", "asc")\
    .get()

print(f"   Clientes brasileiros em ordem alfabética:")
for cliente in resultado['value']:
    print(f"   → {cliente['CompanyName']}")

print("""
💡 DICAS:
-------
• Sempre use .orderby() com .top() para evitar processar milhões de registros
• A ordenação é aplicada ANTES do .top()
• Para ordenar por múltiplos campos: .orderby("Primeiro", "asc").orderby("Segundo", "desc")
  (Veremos nos exemplos avançados)
""")

input("\n⏸️  Pressione ENTER para continuar...")

# ============================================================================
# PARTE 6: PAGINAÇÃO (TOP E SKIP)
# ============================================================================

print("\n" + "="*80)
print(" PARTE 6: PAGINAÇÃO - CONTROLE DE VOLUME DE DADOS".center(80))
print("="*80)

print("""
PAGINANDO RESULTADOS COM .top() e .skip():
----------------------------------------
Quando uma consulta retorna muitos registros, usamos paginação para limitar a resposta.

• .top(n): Retorna apenas os primeiros 'n' registros
• .skip(n): Pula os primeiros 'n' registros

CONCEITO DE PAGINAÇÃO:
--------------------
Página 1: .skip(0).top(10)   → Registros 1-10
Página 2: .skip(10).top(10)  → Registros 11-20
Página 3: .skip(20).top(10)  → Registros 21-30

EXEMPLOS PRÁTICOS:
----------------""")

# EXEMPLO 1: Limitando resultados
print("\n📌 EXEMPLO 1: Limitando a 3 registros (.top(3))")
resultado = client.entity("Products")\
    .select("ProductName")\
    .top(3)\
    .get()

print(f"   Retornou {len(resultado['value'])} produtos:")
for produto in resultado['value']:
    print(f"   → {produto['ProductName']}")

# EXEMPLO 2: Pulando e limitando (página 2)
print("\n📌 EXEMPLO 2: Segunda página (.skip(3).top(3))")
resultado = client.entity("Products")\
    .select("ProductName")\
    .skip(3)\
    .top(3)\
    .get()

print(f"   Retornou {len(resultado['value'])} produtos (página 2):")
for produto in resultado['value']:
    print(f"   → {produto['ProductName']}")

# EXEMPLO 3: Sistema de paginação completo
print("\n📌 EXEMPLO 3: Sistema de paginação completo")
itens_por_pagina = 5
pagina_atual = 1

print(f"   Configuração: {itens_por_pagina} itens por página")
resultado = client.entity("Customers")\
    .select("CustomerID", "CompanyName")\
    .orderby("CompanyName", "asc")\
    .skip((pagina_atual - 1) * itens_por_pagina)\
    .top(itens_por_pagina)\
    .get()

print(f"   Página {pagina_atual} (itens {(pagina_atual-1)*itens_por_pagina+1} a {pagina_atual*itens_por_pagina}):")
for cliente in resultado['value']:
    print(f"   → {cliente['CustomerID']}: {cliente['CompanyName']}")

print("""
🔄 FUNÇÃO DE PAGINAÇÃO GENÉRICA:
-------------------------------
def paginar(client, entidade, pagina, por_pagina):
    return client.entity(entidade)\\
        .skip((pagina-1) * por_pagina)\\
        .top(por_pagina)\\
        .get()

# Uso:
primeira_pagina = paginar(client, "Customers", 1, 10)
segunda_pagina = paginar(client, "Customers", 2, 10)
""")

input("\n⏸️  Pressione ENTER para continuar...")

# ============================================================================
# PARTE 7: SELEÇÃO DE CAMPOS (EQUIVALENTE AO SELECT DO SQL)
# ============================================================================

print("\n" + "="*80)
print(" PARTE 7: SELEÇÃO DE CAMPOS - OTIMIZANDO RESPOSTAS".center(80))
print("="*80)

print("""
SELECIONANDO CAMPOS ESPECÍFICOS COM .select():
--------------------------------------------
O método .select() escolhe quais campos retornar, reduzindo o tráfego de rede.

SINTAXE:
-------
.select("campo1", "campo2", "campo3")

BENEFÍCIOS:
----------
1. Menos dados trafegam na rede
2. Resposta mais rápida
3. Consumo de memória reduzido
4. Melhor performance em dispositivos móveis

EXEMPLO PRÁTICO - COMPARAÇÃO:
---------------------------""")

# Sem select (todos os campos)
print("\n📌 SEM .select(): Retorna TODOS os campos da entidade")
resultado_sem_select = client.entity("Products").top(1).get()
primeiro_produto = resultado_sem_select['value'][0]
print(f"   Número de campos retornados: {len(primeiro_produto.keys())}")
print(f"   Campos: {list(primeiro_produto.keys())[:10]}... (truncado)")

# Com select (apenas 3 campos)
print("\n📌 COM .select(): Retorna APENAS os campos especificados")
resultado_com_select = client.entity("Products")\
    .select("ProductID", "ProductName", "UnitPrice")\
    .top(1)\
    .get()
produto_limitado = resultado_com_select['value'][0]
print(f"   Número de campos retornados: {len(produto_limitado.keys())}")
print(f"   Campos: {list(produto_limitado.keys())}")

print(f"""
📊 COMPARAÇÃO DE PERFORMANCE:
---------------------------
• Sem .select(): {len(primeiro_produto.keys())} campos retornados
• Com .select(): {len(produto_limitado.keys())} campos retornados
• Economia: {len(primeiro_produto.keys()) - len(produto_limitado.keys())} campos (!)

💡 RECOMENDAÇÃO: SEMPRE use .select() para listagens e relatórios!
""")

print("\n📌 EXEMPLO PRÁTICO: Criando um relatório enxuto")
resultado = client.entity("Products")\
    .select("ProductName", "UnitPrice", "UnitsInStock")\
    .filter("UnitsInStock lt 10")\
    .orderby("UnitsInStock", "asc")\
    .top(5)\
    .get()

print(f"   Produtos com baixo estoque (relatório):")
for produto in resultado['value']:
    print(f"   📦 {produto['ProductName'][:35]:35s} | Estoque: {produto['UnitsInStock']:3d} | Preço: US$ {produto['UnitPrice']:.2f}")

input("\n⏸️  Pressione ENTER para continuar...")

# ============================================================================
# PARTE 8: RELACIONAMENTOS (JOIN COM $expand)
# ============================================================================

print("\n" + "="*80)
print(" PARTE 8: RELACIONAMENTOS - CONSULTANDO DADOS RELACIONADOS".center(80))
print("="*80)

print("""
EXPANDINDO RELACIONAMENTOS COM .expand():
---------------------------------------
O método .expand() faz um "JOIN" com entidades relacionadas, similar ao JOIN do SQL.

CONCEITO:
--------
Imagine que temos:
• Pedido (Order) contém CustomerID
• Cliente (Customer) tem informações detalhadas

Sem .expand(): Retorna apenas o CustomerID
Com .expand('Customer'): Retorna todos os dados do cliente dentro do pedido

EXEMPLOS PRÁTICOS:
----------------""")

# EXEMPLO 1: Sem expand (apenas a referência)
print("\n📌 SEM .expand(): Retorna apenas o ID do cliente")
resultado = client.entity("Orders")\
    .select("OrderID", "CustomerID", "OrderDate")\
    .top(3)\
    .get()

print(f"   Pedidos (apenas referência ao cliente):")
for pedido in resultado['value']:
    print(f"   Pedido {pedido['OrderID']} - Cliente ID: {pedido['CustomerID']} (não tem dados do cliente)")

# EXEMPLO 2: Com expand (dados completos)
print("\n📌 COM .expand(): Retorna todos os dados do cliente")
resultado = client.entity("Orders")\
    .select("OrderID", "OrderDate")\
    .expand("Customer")\
    .top(3)\
    .get()

print(f"   Pedidos com dados completos do cliente:")
for pedido in resultado['value']:
    cliente = pedido['Customer']
    print(f"   📦 Pedido {pedido['OrderID']} - Data: {pedido['OrderDate']}")
    print(f"      👤 Cliente: {cliente['CompanyName']} ({cliente['Country']})")

# EXEMPLO 3: Múltiplos expands
print("\n📌 EXPAND MÚLTIPLO: Expandindo Customer e Employee")
print("   Nota: A Northwind não suporta múltiplos expands diretamente,")
print("   mas a sintaxe correta seria: .expand('Customer', 'Employee')")

print("\n📌 EXEMPLO AVANÇADO: Pedidos de clientes brasileiros")
resultado = client.entity("Orders")\
    .select("OrderID", "OrderDate", "Freight")\
    .expand("Customer")\
    .filter("Customer/Country eq 'Brazil'")\
    .orderby("OrderDate", "desc")\
    .top(3)\
    .get()

print(f"   Últimos pedidos de clientes brasileiros:")
for pedido in resultado['value']:
    cliente = pedido['Customer']
    print(f"   🛒 Pedido {pedido['OrderID']} - Data: {pedido['OrderDate']}")
    print(f"      Cliente: {cliente['CompanyName']}")
    print(f"      Frete: US$ {pedido['Freight']:.2f}")

print("""
💡 DICA IMPORTANTE:
-----------------
• Para filtrar por campos da entidade expandida, use 'Entidade/Campo'
  Exemplo: .filter("Customer/Country eq 'Brazil'")
  
• Limite o número de expands para manter a performance
• Cada expand aumenta o volume de dados retornados
""")

input("\n⏸️  Pressione ENTER para continuar...")

# ============================================================================
# PARTE 9: CONTAGEM DE REGISTROS (COUNT)
# ============================================================================

print("\n" + "="*80)
print(" PARTE 9: CONTAGEM - SABENDO QUANTOS REGISTROS EXISTEM".center(80))
print("="*80)

print("""
CONTANDO REGISTROS COM .count() e .count_only():
-----------------------------------------------
Muitas vezes você só precisa saber QUANTOS registros existem, não os dados em si.

MÉTODOS:
-------
1. .count(True): Inclui a contagem junto com os dados
2. .count_only(): Retorna APENAS o número (mais eficiente)

EXEMPLOS PRÁTICOS:
----------------""")

# EXEMPLO 1: Count inclusivo (dados + contagem)
print("\n📌 MODO 1: .count(True) - Retorna dados E contagem")
resultado = client.entity("Products")\
    .filter("UnitPrice gt 50")\
    .count(True)\
    .top(5)\
    .get()

print(f"   Registros retornados: {len(resultado['value'])} (limitado pelo .top(5))")
print(f"   Total disponível no servidor: {resultado.get('@odata.count', 0)}")
print(f"   ⚠️  Note: Total (671) é maior que os 5 retornados!")

# EXEMPLO 2: Count only (apenas número)
print("\n📌 MODO 2: .count_only() - Retorna APENAS o número")
total = client.entity("Products").filter("UnitPrice gt 50").count_only()
print(f"   Total de produtos com preço > 50: {total}")

# EXEMPLO 3: Contagem com filtros
print("\n📌 EXEMPLO PRÁTICO: Estatísticas de produtos")
total_produtos = client.entity("Products").count_only()
produtos_caros = client.entity("Products").filter("UnitPrice gt 100").count_only()
produtos_baratos = client.entity("Products").filter("UnitPrice lt 10").count_only()
produtos_estoque_baixo = client.entity("Products").filter("UnitsInStock lt 5").count_only()

print(f"""
   📊 ESTATÍSTICAS:
   ─────────────────────────────────
   ✅ Total de produtos: {total_produtos}
   💰 Produtos caros (> US$ 100): {produtos_caros}
   🏷️  Produtos baratos (< US$ 10): {produtos_baratos}
   ⚠️  Estoque baixo (< 5 unidades): {produtos_estoque_baixo}
""")

input("\n⏸️  Pressione ENTER para continuar...")

# ============================================================================
# PARTE 10: TRATAMENTO DE ERROS
# ============================================================================

print("\n" + "="*80)
print(" PARTE 10: TRATAMENTO DE ERROS - CÓDIGO ROBUSTO".center(80))
print("="*80)

print("""
TRATANDO ERROS COM TRY-EXCEPT:
---------------------------
Sempre que interagimos com APIs externas, devemos tratar possíveis erros.

EXCEÇÕES DISPONÍVEIS:
-------------------
• S2MODataConnectionError: Falha na conexão (rede, URL inválida)
• S2MODataError: Erro geral na requisição (filtro inválido, campo inexistente)
• S2MODataNotFoundError: Recurso não encontrado (404)
• S2MODataValidationError: Parâmetros inválidos

EXEMPLOS PRÁTICOS:
----------------""")

def consulta_segura():
    """Exemplo de função com tratamento de erros"""
    
    # EXEMPLO 1: Entidade inválida
    print("\n📌 EXEMPLO 1: Tentando acessar entidade inexistente")
    try:
        resultado = client.entity("EntidadeInexistente").top(1).get()
        print("   ❌ Isso não deveria acontecer!")
    except S2MODataError as e:
        print(f"   ✅ Erro capturado: {str(e)[:80]}...")
    
    # EXEMPLO 2: Filtro inválido
    print("\n📌 EXEMPLO 2: Erro em filtro com campo inexistente")
    try:
        resultado = client.entity("Customers")\
            .filter("CampoInexistente eq 'Brazil'")\
            .top(1)\
            .get()
        print("   ❌ Isso não deveria acontecer!")
    except S2MODataError as e:
        print(f"   ✅ Erro capturado: {str(e)[:80]}...")
    
    # EXEMPLO 3: Conexão inválida
    print("\n📌 EXEMPLO 3: URL inválida - teste de conexão")
    try:
        client_erro = S2MClient("https://url-invalida.com/svc/")
        resultado = client_erro.entity("Customers").top(1).get()
        print("   ❌ Isso não deveria acontecer!")
    except S2MODataConnectionError as e:
        print(f"   ✅ Erro de conexão capturado: {str(e)[:80]}...")
    except Exception as e:
        print(f"   ⚠️  Outro erro: {e}")

consulta_segura()

print("""
📝 FUNÇÃO GENÉRICA COM TRATAMENTO DE ERROS:
----------------------------------------
def consultar_com_tratamento(client, entidade, filtro=None):
    try:
        query = client.entity(entidade)
        if filtro:
            query = query.filter(filtro)
        return query.top(100).get()
    except S2MODataConnectionError:
        print("❌ Erro de rede - verifique sua conexão")
        return None
    except S2MODataNotFoundError:
        print(f"❌ Entidade '{entidade}' não encontrada")
        return None
    except S2MODataError as e:
        print(f"❌ Erro na consulta: {e}")
        return None
""")

input("\n⏸️  Pressione ENTER para continuar...")

# ============================================================================
# PARTE 11: PERFORMANCE E BOAS PRÁTICAS
# ============================================================================

print("\n" + "="*80)
print(" PARTE 11: PERFORMANCE E BOAS PRÁTICAS".center(80))
print("="*80)

print("""
OTIMIZANDO SUAS CONSULTAS:
------------------------
Boas práticas para garantir performance e eficiência.

1️⃣ SEMPRE use .select() para campos específicos
2️⃣ Use .top() durante desenvolvimento
3️⃣ Coloque filtros restritivos PRIMEIRO
4️⃣ Use .count_only() quando só precisar do número
5️⃣ Evite .expand() desnecessários
6️⃣ Reutilize o cliente para múltiplas consultas
""")

# Teste de performance comparativo
print("\n📊 TESTE DE PERFORMANCE:")
print("   Comparando consultas com e sem otimização\n")

# Consulta NÃO otimizada
print("   🔴 SEM otimização (todos campos, sem filtros):")
start = time.time()
resultado_lento = client.entity("Products").get()
tempo_lento = time.time() - start
print(f"      Tempo: {tempo_lento:.3f}s - Dados: {len(resultado_lento['value'])} registros")

# Consulta OTIMIZADA
print("\n   🟢 COM otimização (select + filtro + top):")
start = time.time()
resultado_rapido = client.entity("Products")\
    .select("ProductName", "UnitPrice")\
    .filter("UnitPrice gt 50")\
    .top(100)\
    .get()
tempo_rapido = time.time() - start
print(f"      Tempo: {tempo_rapido:.3f}s - Dados: {len(resultado_rapido['value'])} registros")

print(f"\n   📈 ECONOMIA: {((tempo_lento - tempo_rapido) / tempo_lento * 100):.1f}% mais rápido!")

print("""
💡 DICAS DE PERFORMANCE ADICIONAIS:
-----------------------------------
• Cache: Guarde resultados que não mudam com frequência
• Paginação: Processe grandes volumes em lotes
• Filtros: Quanto mais específico o filtro, mais rápido
• Limite: Use .top() mesmo em produção
""")

input("\n⏸️  Pressione ENTER para continuar...")

# ============================================================================
# PARTE 12: EXEMPLOS AVANÇADOS E CASOS REAIS
# ============================================================================

print("\n" + "="*80)
print(" PARTE 12: EXEMPLOS AVANÇADOS - CASOS REAIS".center(80))
print("="*80)

print("""
CASOS DE USO REAIS:
-----------------
1. Dashboard de Vendas
2. Relatório de Estoque
3. Sistema de Busca
4. Monitoramento de Pedidos
""")

# CASO 1: Dashboard de vendas
print("\n📊 CASO 1: Dashboard de Vendas")
print("   ─────────────────────────────")

# Total de clientes por país
print("   🌍 Top 5 países com mais clientes:")
paises = {}
clientes_totais = client.entity("Customers").get()
for cliente in clientes_totais['value']:
    pais = cliente['Country']
    paises[pais] = paises.get(pais, 0) + 1

top_paises = sorted(paises.items(), key=lambda x: x[1], reverse=True)[:5]
for i, (pais, total) in enumerate(top_paises, 1):
    print(f"      {i}. {pais}: {total} clientes")

# CASO 2: Relatório de estoque crítico
print("\n⚠️  CASO 2: Estoque Crítico")
print("   ─────────────────────────")

produtos_criticos = client.entity("Products")\
    .select("ProductName", "UnitsInStock", "UnitPrice")\
    .filter("UnitsInStock lt 10")\
    .orderby("UnitsInStock", "asc")\
    .top(5)\
    .get()

print("   Produtos com estoque baixo:")
for produto in produtos_criticos['value']:
    print(f"      📦 {produto['ProductName'][:35]:35s} | Estoque: {produto['UnitsInStock']:3d} | Preço: US$ {produto['UnitPrice']:.2f}")

# CASO 3: Sistema de busca avançada
print("\n🔍 CASO 3: Busca de Produtos")
print("   ──────────────────────────")

termo_busca = "Chai"
print(f"   Buscando por: '{termo_busca}'")

produtos_busca = client.entity("Products")\
    .select("ProductName", "UnitPrice", "QuantityPerUnit")\
    .filter(f"contains(ProductName, '{termo_busca}')")\
    .get()

if produtos_busca['value']:
    print(f"   ✅ Encontrados {len(produtos_busca['value'])} produtos:")
    for produto in produtos_busca['value']:
        print(f"      → {produto['ProductName']}")
        print(f"        Preço: US$ {produto['UnitPrice']} | Embalagem: {produto['QuantityPerUnit']}")
else:
    print(f"   ❌ Nenhum produto encontrado com '{termo_busca}'")

# CASO 4: Monitoramento de pedidos
print("\n📋 CASO 4: Últimos Pedidos")
print("   ────────────────────────")

pedidos_recentes = client.entity("Orders")\
    .select("OrderID", "OrderDate", "Freight")\
    .expand("Customer")\
    .orderby("OrderDate", "desc")\
    .top(3)\
    .get()

print("   Últimos 3 pedidos realizados:")
for pedido in pedidos_recentes['value']:
    cliente = pedido['Customer']
    print(f"      🛒 Pedido #{pedido['OrderID']} - {pedido['OrderDate']}")
    print(f"         Cliente: {cliente['CompanyName']}")
    print(f"         Frete: US$ {pedido['Freight']:.2f}")

input("\n⏸️  Pressione ENTER para continuar...")

# ============================================================================
# PARTE 13: DESAFIOS PARA VOCÊ PRATICAR
# ============================================================================

print("\n" + "="*80)
print(" PARTE 13: DESAFIOS - AGORA É SUA VEZ!".center(80))
print("="*80)

print("""
🎯 DESAFIO 1: Fácil
─────────────────
"Liste os 10 produtos mais caros da categoria 'Beverages'"

Dicas:
• Entidade: Products
• Campos: ProductName, UnitPrice, CategoryID
• Filtro: "CategoryID eq 1" (Beverages)
• Ordenação: por preço decrescente

─────────────────────────────────────────────────

🎯 DESAFIO 2: Intermediário
─────────────────────────
"Calcule o valor total do frete de pedidos para clientes brasileiros"

Dicas:
• Entidade: Orders
• Campos: Freight, Customer/Country
• Expand: Customer
• Filtro: "Customer/Country eq 'Brazil'"

─────────────────────────────────────────────────

🎯 DESAFIO 3: Avançado
─────────────────────
"Crie um relatório de produtos que precisam ser reabastecidos:
 - Estoque menor que 10 OU
 - Estoque é menor que o pedido mínimo (ReorderLevel)"

Dicas:
• Use AND/OR no filtro
• Compare UnitsInStock com ReorderLevel
• Ordenação: por estoque crescente

─────────────────────────────────────────────────

🎯 DESAFIO 4: Expert
───────────────────
"Implemente um sistema de paginação que:
 - Mostre 20 itens por página
 - Calcule quantas páginas existem no total
 - Permita navegar entre as páginas"

Dicas:
• Use .count_only() para total
• Use .skip() e .top() para paginação
• Armazene resultados em cache

─────────────────────────────────────────────────
""")

# Adicionando um exemplo de solução do desafio 1
print("\n💡 SOLUÇÃO DO DESAFIO 1 (para referência):")
print("   client.entity('Products')")
print("       .select('ProductName', 'UnitPrice')")
print("       .filter(\"CategoryID eq 1\")")
print("       .orderby('UnitPrice', 'desc')")
print("       .top(10)")
print("       .get()")

print(f"""
================================================================================
                          FIM DO TUTORIAL
================================================================================

📚 RESUMO DO QUE VOCÊ APRENDEU:
─────────────────────────────
✅ Inicializar o cliente S2MOdataPy
✅ Fazer consultas básicas com .get()
✅ Filtrar dados com .filter()
✅ Ordenar resultados com .orderby()
✅ Paginar com .top() e .skip()
✅ Selecionar campos com .select()
✅ Expandir relacionamentos com .expand()
✅ Contar registros com .count() e .count_only()
✅ Tratar erros corretamente
✅ Otimizar performance

🚀 PRÓXIMOS PASSOS:
─────────────────
1. Pratique os desafios propostos
2. Explore outras entidades (Employees, Suppliers, Categories)
3. Integre com pandas para análise de dados
4. Crie dashboards usando os dados do OData
5. Contribua com a biblioteca S2MOdataPy

📖 RECURSOS ADICIONAIS:
─────────────────────
• Documentação oficial OData: https://www.odata.org/
• Exemplos na pasta examples/ do projeto
• Testes unitários para referência

👋 OBRIGADO POR ESTUDAR COM S2MODATAPY!
────────────────────────────────────────
Criado por: Christopher N. S. M. Mauricio
Licença: MIT with Attribution
GitHub: https://github.com/ChristopherNicolasSMM/S2MOdataPy

Se este tutorial foi útil, dê uma estrela no GitHub! ⭐

================================================================================
""")

# ============================================================================
# EXECUÇÃO AUTOMÁTICA (opcional - descomente para rodar tudo)
# ============================================================================

if __name__ == "__main__":
    print("\n🎯 Tutorial completo do S2MOdataPy carregado!")
    print("Execute cada seção pressionando ENTER conforme solicitado.")
    print("Divirta-se aprendendo! 🚀")