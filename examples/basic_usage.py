"""
Exemplos de uso da biblioteca S2MOdataPy

Demonstra as principais funcionalidades:
- Consultas com filtros, ordenação e paginação
- Operações de escrita (criar, atualizar, deletar)
- Leitura de metadados e anotações de UI
- Uso com autenticação

Para executar este arquivo, o servidor de demonstração deve estar
rodando em http://localhost:8000

Author: Christopher N. S. M. Mauricio
"""

from s2modatapy import S2MClient, S2MODataError, S2MODataConnectionError


def exemplo_leitura_basica():
    """Consultas simples de leitura."""
    print("\n── Leitura básica ───────────────────────────────")
    client = S2MClient("http://localhost:8000/odata/", debug=True)

    # Buscar todos os clientes (respeitando paginação padrão do servidor)
    result = client.entity("Customers").get()
    print(f"Total na página: {len(result.get('value', []))}")

    # Filtro por país com limite
    result = (
        client.entity("Customers")
        .filter("Country eq 'Mexico'")
        .orderby("CompanyName")
        .top(5)
        .get()
    )
    for c in result.get("value", []):
        print(f"  {c['CustomerID']} — {c['CompanyName']}")

    # Primeiro registro
    primeiro = client.entity("Customers").orderby("CustomerID").first()
    print(f"\nPrimeiro: {primeiro}")


def exemplo_paginacao():
    """Paginação de resultados."""
    print("\n── Paginação ────────────────────────────────────")
    client = S2MClient("http://localhost:8000/odata/")

    # Total de registros
    total = client.entity("Customers").count_only()
    print(f"Total de clientes: {total}")

    # Navegar páginas
    for pg in range(1, 4):
        result = client.entity("Customers").page(pg, page_size=10)
        registros = result.get("value", [])
        print(f"  Página {pg}: {len(registros)} registros")


def exemplo_escrita():
    """Criar, atualizar e deletar registros."""
    print("\n── Escrita (CRUD) ───────────────────────────────")
    client = S2MClient("http://localhost:8000/odata/")

    # Criar
    novo = client.entity("Customers").create({
        "CustomerID": "TSTBR",
        "CompanyName": "Empresa de Teste",
        "ContactName": "Fulano de Tal",
        "Country": "Brazil",
    })
    print(f"Criado: {novo}")

    # Atualização parcial (PATCH)
    client.entity("Customers").patch("TSTBR", {
        "ContactName": "Fulano Atualizado"
    })
    print("Registro atualizado (PATCH)")

    # Substituição completa (PUT)
    client.entity("Customers").update("TSTBR", {
        "CustomerID": "TSTBR",
        "CompanyName": "Empresa de Teste Renomeada",
        "Country": "Brazil",
    })
    print("Registro substituído (PUT)")

    # Deletar
    client.entity("Customers").delete("TSTBR")
    print("Registro deletado")


def exemplo_metadados():
    """Ler metadados e anotações de UI do servidor."""
    print("\n── Metadados e anotações de UI ──────────────────")
    client = S2MClient("http://localhost:8000/odata/")

    # Listar entidades disponíveis
    entidades = client.list_entities()
    print(f"Entidades: {entidades}")

    # Anotações de uma entidade
    ann = client.get_ui_annotations("Customer")
    print(f"\nEntidade : {ann.entity_name}")
    print(f"Label    : {ann.label}")

    if ann.list_view:
        print(f"\nColunas da listagem:")
        for col in ann.list_view.columns:
            flags = []
            if col.sortable:   flags.append("sortable")
            if col.filterable: flags.append("filterable")
            if col.required:   flags.append("required")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            print(f"  {col.label:20s} ({col.name}){flag_str}")
        print(f"\nOrdenação padrão: {ann.list_view.default_sort}")

    if ann.form:
        print(f"\nGrupos de formulário:")
        for group in ann.form.groups:
            print(f"  [{group.label}]")
            for f in group.fields:
                req = " *" if f.required else ""
                print(f"    - {f.label}{req}")

    if ann.validations:
        print(f"\nValidações:")
        for campo, regras in ann.validations.items():
            for r in regras:
                print(f"  {campo}: {r['type']} — {r['message']}")

    # Config JSON pronta para uso em componentes
    from s2modatapy.parsers.annotations import ODataAnnotationParser
    metadata = client.get_metadata_json()
    parser = ODataAnnotationParser.from_dict(metadata)
    config = parser.to_ui_config("Customer")
    print(f"\nConfig UI (dict): {list(config.keys())}")


def exemplo_autenticacao():
    """Uso com autenticação Basic e Bearer."""
    print("\n── Autenticação ─────────────────────────────────")

    # Basic Auth
    client_basic = S2MClient(
        "http://meu-servidor/odata/",
        auth=("usuario", "senha"),
    )
    print(f"Basic Auth configurado: {client_basic.session.auth}")

    # Bearer Token
    client_bearer = S2MClient(
        "http://meu-servidor/odata/",
        bearer_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    print(f"Bearer configurado: {client_bearer.session.headers.get('Authorization', '')[:30]}...")


def exemplo_tratamento_erros():
    """Captura e tratamento de erros."""
    print("\n── Tratamento de erros ──────────────────────────")
    client = S2MClient("http://localhost:8000/odata/")

    try:
        client.entity("EntidadeInexistente").get()
    except S2MODataConnectionError as e:
        print(f"Servidor inacessível: {e}")
    except S2MODataError as e:
        print(f"Erro OData: {e}")
        if e.details:
            print(f"  Detalhes: {e.details}")


if __name__ == "__main__":
    try:
        exemplo_leitura_basica()
        exemplo_paginacao()
        exemplo_metadados()
        exemplo_autenticacao()
        exemplo_tratamento_erros()
        # exemplo_escrita()  # Descomente para testar escrita
    except S2MODataConnectionError:
        print("\n[Aviso] Servidor não está rodando. Execute o DemoAnotation primeiro.")
        print("  cd DemoAnotation && uvicorn main:app --reload")
