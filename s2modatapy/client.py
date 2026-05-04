"""
Módulo principal do cliente S2MOdataPy

Author: Christopher N. S. M. Mauricio
"""

import requests
from typing import Dict, Any, Optional, Tuple
from .query_builder import ODataQueryBuilder
from .debug import DebugMonitor
from .exceptions import (
    S2MODataError,
    S2MODataConnectionError,
    S2MODataNotFoundError,
    S2MODataAuthenticationError,
)


class S2MClient:
    """
    Cliente principal para serviços OData V4.

    Suporta consultas (GET), escrita (POST/PUT/PATCH/DELETE),
    leitura de metadados com anotações de UI e autenticação
    via Basic Auth ou Bearer Token.

    Attributes:
        base_url (str): URL base do serviço OData.
        debug (bool): Ativa saída de debug detalhada.
        session (requests.Session): Sessão HTTP reutilizada entre chamadas.

    Exemplo básico:
        client = S2MClient("http://localhost:8000/odata/")
        result = client.entity("Customers").filter("Country eq 'Brazil'").top(10).get()

    Exemplo com autenticação:
        client = S2MClient(
            "http://meu-servidor/odata/",
            auth=("usuario", "senha")
        )

    Exemplo lendo metadados:
        annotations = client.get_ui_annotations("Customers")
        print(annotations.label)
        print(annotations.list_view.columns)
    """

    def __init__(
        self,
        base_url: str,
        debug: bool = False,
        auth: Optional[Tuple[str, str]] = None,
        bearer_token: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Inicializa o cliente OData.

        Args:
            base_url (str): URL base do serviço OData.
            debug (bool): Ativa modo debug (exibe URLs e cabeçalhos).
            auth (tuple, optional): Credenciais Basic Auth como (usuario, senha).
            bearer_token (str, optional): Token Bearer para autenticação por header.
            timeout (int): Timeout em segundos para todas as requisições. Padrão: 30.
        """
        self.base_url = base_url.rstrip("/")
        self.debug = debug
        self.timeout = timeout
        self.session = requests.Session()
        self.debug_monitor = DebugMonitor(debug)

        # Cabeçalhos padrão
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "S2MOdataPy/0.2.0",
            }
        )

        # Autenticação Basic
        if auth is not None:
            self.session.auth = auth

        # Autenticação Bearer
        if bearer_token is not None:
            self.session.headers.update(
                {"Authorization": f"Bearer {bearer_token}"}
            )

        if debug:
            print(f"[S2MOdataPy] Cliente inicializado")
            print(f"[S2MOdataPy] Base URL: {self.base_url}")
            auth_mode = "Bearer" if bearer_token else ("Basic" if auth else "Nenhuma")
            print(f"[S2MOdataPy] Autenticação: {auth_mode}")

    # ─────────────────────────────────────────────────────────────────────────
    # Interface pública — consultas
    # ─────────────────────────────────────────────────────────────────────────

    def entity(self, entity_name: str) -> ODataQueryBuilder:
        """
        Inicia um builder de consulta para uma entidade.

        Args:
            entity_name (str): Nome da entidade (ex: 'Customers', 'Orders').

        Returns:
            ODataQueryBuilder: Builder fluente para construção e execução da query.

        Exemplo:
            result = client.entity("Customers").filter("Country eq 'Brazil'").get()
        """
        return ODataQueryBuilder(self, entity_name)

    # ─────────────────────────────────────────────────────────────────────────
    # Interface pública — metadados e anotações
    # ─────────────────────────────────────────────────────────────────────────

    def get_metadata_json(self) -> dict:
        """
        Busca os metadados do serviço no formato JSON enriquecido.

        Requer que o servidor exponha o endpoint `/$metadata.json`.
        Esse endpoint retorna as anotações de UI (lista, formulário,
        validações) em formato JSON de fácil consumo.

        Returns:
            dict: Dicionário com metadados completos do serviço.

        Raises:
            S2MODataConnectionError: Falha na conexão com o servidor.
            S2MODataError: Erro na requisição.
        """
        return self._request("GET", "$metadata.json")

    def get_ui_annotations(self, entity_name: str):
        """
        Retorna as anotações de UI para uma entidade específica,
        lendo os metadados do servidor.

        Args:
            entity_name (str): Nome da entidade (ex: 'Customers').

        Returns:
            UIAnnotations: Objeto com configuração de lista, formulário
                           e validações da entidade. Retorna objeto vazio
                           se a entidade não for encontrada nos metadados.

        Exemplo:
            ann = client.get_ui_annotations("Customers")
            for col in ann.list_view.columns:
                print(col.label, col.sortable)
        """
        from .parsers.annotations import ODataAnnotationParser

        metadata = self.get_metadata_json()
        parser = ODataAnnotationParser.from_dict(metadata)
        return parser.parse_entity(entity_name)

    def list_entities(self):
        """
        Retorna os nomes de todas as entidades disponíveis no serviço.

        Returns:
            list[str]: Lista com nomes das entidades.
        """
        from .parsers.annotations import ODataAnnotationParser

        metadata = self.get_metadata_json()
        parser = ODataAnnotationParser.from_dict(metadata)
        return parser.get_all_entities()

    # ─────────────────────────────────────────────────────────────────────────
    # Interface interna — HTTP
    # ─────────────────────────────────────────────────────────────────────────

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        data: Dict = None,
    ) -> Dict[str, Any]:
        """
        Executa uma requisição HTTP ao serviço OData.

        Args:
            method (str): Método HTTP (GET, POST, PUT, PATCH, DELETE).
            endpoint (str): Caminho relativo à URL base.
            params (dict, optional): Parâmetros de query string ($filter, $select, etc.).
            data (dict, optional): Corpo da requisição para POST/PUT/PATCH.

        Returns:
            dict: Resposta JSON deserializada do servidor.

        Raises:
            S2MODataConnectionError: Impossível conectar ao servidor.
            S2MODataAuthenticationError: Credenciais inválidas (401/403).
            S2MODataNotFoundError: Recurso não encontrado (404).
            S2MODataError: Qualquer outro erro HTTP ou de processamento.
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            if self.debug:
                self.debug_monitor.log_request(method, url, params, data)

            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data if method in ["POST", "PUT", "PATCH"] else None,
                timeout=self.timeout,
            )

            if self.debug:
                self.debug_monitor.log_response(response)

            # Tratamento de status HTTP específicos
            if response.status_code in (401, 403):
                raise S2MODataAuthenticationError(
                    f"Autenticação falhou ({response.status_code}). "
                    "Verifique as credenciais."
                )
            if response.status_code == 404:
                raise S2MODataNotFoundError(
                    f"Recurso não encontrado: {endpoint}"
                )

            response.raise_for_status()

            # Resposta vazia (ex: DELETE bem-sucedido)
            if not response.content:
                return {}

            return response.json()

        except requests.exceptions.ConnectionError as e:
            raise S2MODataConnectionError(
                f"Falha na conexão com '{self.base_url}': {e}"
            )
        except (S2MODataAuthenticationError, S2MODataNotFoundError):
            raise
        except requests.exceptions.HTTPError as e:
            raise S2MODataError(
                f"Erro HTTP {response.status_code}: {e}",
                details={"status_code": response.status_code, "url": url},
            )
        except Exception as e:
            raise S2MODataError(f"Erro inesperado: {e}")
