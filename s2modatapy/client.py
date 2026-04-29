"""
Módulo principal do cliente S2MOdataPy
Author: Christopher N. S. M. Mauricio
"""

import requests
from typing import Dict, Any, Optional
from .query_builder import ODataQueryBuilder
from .debug import DebugMonitor
from .exceptions import S2MODataError, S2MODataConnectionError


class S2MClient:
    """
    Cliente principal para serviços OData V4
    
    Attributes:
        base_url: URL base do serviço OData
        debug: Modo debug (True/False)
        response_format: Formato da resposta ('json' ou 'xml')
        session: Sessão requests para persistência de conexão
    """
    
    def __init__(self, base_url: str, debug: bool = False, 
                 response_format: str = 'json'):
        """
        Inicializa o cliente OData
        
        Args:
            base_url: URL base do serviço OData
            debug: Ativa modo debug (mostra URLs e cabeçalhos)
            response_format: Formato da resposta ('json' ou 'xml')
        """
        self.base_url = base_url.rstrip('/')
        self.debug = debug
        self.response_format = response_format if response_format in ['json', 'xml'] else 'json'
        self.session = requests.Session()
        self.debug_monitor = DebugMonitor(debug)
        
        # Set default headers
        self.session.headers.update({
            'Accept': 'application/json' if self.response_format == 'json' else 'application/xml',
            'User-Agent': f'S2MOdataPy/0.1.0 (C) Christopher N. S. M. Mauricio'
        })
        
        if debug:
            print(f"[S2MOdataPy] Cliente inicializado por Christopher N. S. M. Mauricio")
            print(f"[S2MOdataPy] Base URL: {self.base_url}")
            print(f"[S2MOdataPy] Formato: {self.response_format.upper()}")
    
    def entity(self, entity_name: str) -> ODataQueryBuilder:
        """
        Inicia uma query para uma entidade específica
        
        Args:
            entity_name: Nome da entidade (ex: 'Customers', 'Orders')
            
        Returns:
            ODataQueryBuilder: Builder para construção da query
        """
        return ODataQueryBuilder(self, entity_name)
    
    def _request(self, method: str, endpoint: str, params: Dict = None, 
                 data: Dict = None) -> Dict[str, Any]:
        """
        Método interno para realizar requisições HTTP
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE, PATCH)
            endpoint: Endpoint da API
            params: Parâmetros da query string ($filter, $select, etc)
            data: Dados para envio (POST/PUT/PATCH)
            
        Returns:
            Dicionário com a resposta do servidor
            
        Raises:
            S2MODataConnectionError: Erro de conexão
            S2MODataError: Erro na requisição OData
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if self.debug:
                self.debug_monitor.log_request(method, url, params, data)
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data if method in ['POST', 'PUT', 'PATCH'] else None,
                timeout=30
            )
            
            if self.debug:
                self.debug_monitor.log_response(response)
            
            response.raise_for_status()
            
            if self.response_format == 'json':
                return response.json()
            else:
                # XML parsing será implementado depois
                return {'value': []}
                
        except requests.exceptions.ConnectionError as e:
            raise S2MODataConnectionError(f"Falha na conexão: {e}")
        except requests.exceptions.HTTPError as e:
            raise S2MODataError(f"Erro HTTP {response.status_code}: {e}")
        except Exception as e:
            raise S2MODataError(f"Erro inesperado: {e}")