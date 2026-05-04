"""
Módulo de Query Builder para OData V4

Author: Christopher N. S. M. Mauricio
"""

from typing import Dict, Any, Optional, List


class ODataQueryBuilder:
    """
    Construtor fluente de queries OData V4.

    Suporta todas as operações de leitura ($filter, $select, $orderby,
    $top, $skip, $expand, $count) e escrita (POST, PUT, PATCH, DELETE).

    Exemplo de leitura:
        result = (
            client.entity("Customers")
            .select("CustomerID", "CompanyName")
            .filter("Country eq 'Brazil'")
            .orderby("CompanyName")
            .top(10)
            .get()
        )

    Exemplo de escrita:
        novo = client.entity("Customers").create({
            "CustomerID": "BRASI",
            "CompanyName": "Brasil Ltda",
            "Country": "Brazil"
        })

        client.entity("Customers").update("BRASI", {"CompanyName": "Brasil S.A."})

        client.entity("Customers").delete("BRASI")
    """

    def __init__(self, client, entity_name: str):
        """
        Inicializa o builder.

        Args:
            client: Instância do cliente S2MClient.
            entity_name (str): Nome da entidade a ser consultada/modificada.
        """
        self.client = client
        self.entity_name = entity_name
        self.params: Dict[str, Any] = {}

    # ─────────────────────────────────────────────────────────────────────────
    # Métodos de leitura — retornam self para encadeamento
    # ─────────────────────────────────────────────────────────────────────────

    def select(self, *fields: str) -> "ODataQueryBuilder":
        """
        Define quais campos retornar na resposta ($select).

        Args:
            *fields (str): Nomes dos campos desejados.

        Returns:
            ODataQueryBuilder: Self para encadeamento.

        Exemplo:
            .select("CustomerID", "CompanyName", "Country")
        """
        if fields:
            self.params["$select"] = ",".join(fields)
        return self

    def filter(self, condition: str) -> "ODataQueryBuilder":
        """
        Aplica condição de filtro na consulta ($filter).

        Suporta operadores OData: eq, ne, gt, ge, lt, le, contains.

        Args:
            condition (str): Expressão de filtro no formato OData.

        Returns:
            ODataQueryBuilder: Self para encadeamento.

        Exemplos:
            .filter("Country eq 'Brazil'")
            .filter("Price gt 100")
            .filter("contains(CompanyName, 'Tech')")
        """
        self.params["$filter"] = condition
        return self

    def orderby(self, field: str, direction: str = "asc") -> "ODataQueryBuilder":
        """
        Define ordenação dos resultados ($orderby).

        Args:
            field (str): Campo para ordenação.
            direction (str): 'asc' (padrão) ou 'desc'.

        Returns:
            ODataQueryBuilder: Self para encadeamento.

        Exemplo:
            .orderby("CompanyName", "desc")
        """
        direction = direction.lower()
        if direction not in ("asc", "desc"):
            direction = "asc"
        self.params["$orderby"] = f"{field} {direction}"
        return self

    def orderby_multi(self, *fields: str) -> "ODataQueryBuilder":
        """
        Define ordenação por múltiplos campos ($orderby).

        Args:
            *fields (str): Expressões de ordenação no formato 'campo dir'.

        Returns:
            ODataQueryBuilder: Self para encadeamento.

        Exemplo:
            .orderby_multi("Country asc", "CompanyName desc")
        """
        if fields:
            self.params["$orderby"] = ",".join(fields)
        return self

    def top(self, n: int) -> "ODataQueryBuilder":
        """
        Limita o número de registros retornados ($top).

        Args:
            n (int): Número máximo de registros. Deve ser >= 0.

        Returns:
            ODataQueryBuilder: Self para encadeamento.
        """
        if n >= 0:
            self.params["$top"] = n
        return self

    def skip(self, n: int) -> "ODataQueryBuilder":
        """
        Pula N registros na resposta — usado para paginação ($skip).

        Args:
            n (int): Número de registros a ignorar. Deve ser >= 0.

        Returns:
            ODataQueryBuilder: Self para encadeamento.

        Exemplo (página 3 com 20 itens/página):
            .top(20).skip(40).get()
        """
        if n >= 0:
            self.params["$skip"] = n
        return self

    def expand(self, *entities: str) -> "ODataQueryBuilder":
        """
        Expande entidades relacionadas na resposta ($expand).

        Args:
            *entities (str): Nomes das navegações a expandir.

        Returns:
            ODataQueryBuilder: Self para encadeamento.

        Exemplo:
            .expand("Orders", "Orders/OrderDetails")
        """
        if entities:
            self.params["$expand"] = ",".join(entities)
        return self

    def count(self, enabled: bool = True) -> "ODataQueryBuilder":
        """
        Solicita a contagem total de registros junto à resposta ($count).

        O total é retornado no campo '@odata.count' da resposta, independente
        da paginação aplicada por $top/$skip.

        Args:
            enabled (bool): True para incluir contagem total. Padrão: True.

        Returns:
            ODataQueryBuilder: Self para encadeamento.
        """
        self.params["$count"] = str(enabled).lower()
        return self

    # ─────────────────────────────────────────────────────────────────────────
    # Métodos de execução — terminam o encadeamento
    # ─────────────────────────────────────────────────────────────────────────

    def get(self) -> Dict[str, Any]:
        """
        Executa a consulta GET com todos os parâmetros configurados.

        Returns:
            dict: Resposta completa do servidor. Registros em ['value'],
                  total em ['@odata.count'] (se count() foi chamado).
        """
        return self.client._request("GET", self.entity_name, params=self.params)

    def first(self) -> Optional[Dict[str, Any]]:
        """
        Retorna apenas o primeiro registro ($top=1).

        Returns:
            dict | None: Primeiro registro encontrado, ou None se vazio.
        """
        self.top(1)
        result = self.get()
        values = result.get("value", [])
        return values[0] if values else None

    def count_only(self) -> int:
        """
        Retorna apenas a contagem total de registros que atendem ao filtro.

        Internamente usa $count=true e $top=0 para evitar tráfego de dados.

        Returns:
            int: Total de registros disponíveis com o filtro atual.
        """
        self.count(True).top(0)
        result = self.get()
        return result.get("@odata.count", 0)

    def page(self, page_number: int, page_size: int = 20) -> Dict[str, Any]:
        """
        Atalho para paginação: define $top e $skip a partir de
        número de página (base 1) e tamanho de página.

        Args:
            page_number (int): Número da página desejada (começa em 1).
            page_size (int): Registros por página. Padrão: 20.

        Returns:
            dict: Resposta do servidor para a página solicitada.

        Exemplo:
            # Busca a segunda página com 10 itens
            result = client.entity("Products").page(2, 10).get()
        """
        if page_number < 1:
            page_number = 1
        return self.top(page_size).skip((page_number - 1) * page_size).get()

    # ─────────────────────────────────────────────────────────────────────────
    # Métodos de escrita
    # ─────────────────────────────────────────────────────────────────────────

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um novo registro na entidade (POST).

        Args:
            data (dict): Dicionário com os campos e valores do novo registro.

        Returns:
            dict: Registro criado conforme retornado pelo servidor.

        Exemplo:
            novo = client.entity("Customers").create({
                "CustomerID": "BRASI",
                "CompanyName": "Brasil Ltda",
                "Country": "Brazil"
            })
        """
        return self.client._request("POST", self.entity_name, data=data)

    def update(self, key: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Substitui completamente um registro existente (PUT).

        Em OData V4, PUT exige que todos os campos editáveis sejam enviados;
        campos omitidos podem ser zerados pelo servidor.
        Para atualização parcial, use patch().

        Args:
            key: Valor da chave primária do registro. Strings são citadas
                 automaticamente na URL (ex: 'ALFKI' → Customers('ALFKI')).
                 Inteiros são enviados sem aspas (ex: 1 → Orders(1)).
            data (dict): Dados completos do registro.

        Returns:
            dict: Resposta do servidor (pode ser vazia em 204 No Content).

        Exemplo:
            client.entity("Customers").update("BRASI", {
                "CompanyName": "Brasil S.A.",
                "Country": "Brazil"
            })
        """
        endpoint = self._build_key_endpoint(key)
        return self.client._request("PUT", endpoint, data=data)

    def patch(self, key: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza parcialmente um registro (PATCH).

        Apenas os campos presentes em data são alterados.
        Os demais campos permanecem intocados.

        Args:
            key: Valor da chave primária do registro.
            data (dict): Dicionário com apenas os campos a atualizar.

        Returns:
            dict: Resposta do servidor.

        Exemplo:
            client.entity("Customers").patch("BRASI", {
                "ContactName": "João Silva"
            })
        """
        endpoint = self._build_key_endpoint(key)
        return self.client._request("PATCH", endpoint, data=data)

    def delete(self, key: Any) -> bool:
        """
        Remove um registro da entidade (DELETE).

        Args:
            key: Valor da chave primária do registro a remover.

        Returns:
            bool: True se removido com sucesso.

        Raises:
            S2MODataNotFoundError: Registro não encontrado.

        Exemplo:
            client.entity("Customers").delete("BRASI")
        """
        endpoint = self._build_key_endpoint(key)
        self.client._request("DELETE", endpoint)
        return True

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers internos
    # ─────────────────────────────────────────────────────────────────────────

    def _build_key_endpoint(self, key: Any) -> str:
        """
        Monta o endpoint com a chave primária no formato OData.

        Strings são citadas: Customers('ALFKI')
        Inteiros sem aspas:  Orders(1)
        """
        if isinstance(key, str):
            return f"{self.entity_name}('{key}')"
        return f"{self.entity_name}({key})"
