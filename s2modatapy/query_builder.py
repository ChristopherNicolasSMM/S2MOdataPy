"""
Módulo de Query Builder para OData
Author: Christopher N. S. M. Mauricio
"""

from typing import Dict, Any, Optional, List, Union


class ODataQueryBuilder:
    """
    Construtor fluente de queries OData
    
    Exemplo:
        query = (client.entity("Customers")
                 .select("CustomerID", "CompanyName")
                 .filter("Country eq 'Brazil'")
                 .top(10)
                 .get())
    """
    
    def __init__(self, client, entity_name: str):
        """
        Inicializa o query builder
        
        Args:
            client: Instância do cliente S2MClient
            entity_name: Nome da entidade a ser consultada
        """
        self.client = client
        self.entity_name = entity_name
        self.params = {}
    
    def select(self, *fields: str) -> 'ODataQueryBuilder':
        """
        Seleciona quais campos retornar ($select)
        
        Args:
            *fields: Nomes dos campos a serem retornados
            
        Returns:
            self: Para encadeamento de métodos
        """
        if fields:
            self.params['$select'] = ','.join(fields)
        return self
    
    def filter(self, condition: str) -> 'ODataQueryBuilder':
        """
        Aplica filtro na consulta ($filter)
        
        Args:
            condition: Condição de filtro (ex: "Country eq 'Brazil'")
            
        Returns:
            self: Para encadeamento de métodos
        """
        self.params['$filter'] = condition
        return self
    
    def orderby(self, field: str, direction: str = 'asc') -> 'ODataQueryBuilder':
        """
        Ordena os resultados ($orderby)
        
        Args:
            field: Campo para ordenação
            direction: Direção ('asc' ou 'desc')
            
        Returns:
            self: Para encadeamento de métodos
        """
        self.params['$orderby'] = f"{field} {direction}"
        return self
    
    def top(self, n: int) -> 'ODataQueryBuilder':
        """
        Limita o número de resultados ($top)
        
        Args:
            n: Número máximo de registros a retornar
            
        Returns:
            self: Para encadeamento de métodos
        """
        if n > 0:
            self.params['$top'] = n
        return self
    
    def skip(self, n: int) -> 'ODataQueryBuilder':
        """
        Pula N resultados ($skip) - usado para paginação
        
        Args:
            n: Número de registros a pular
            
        Returns:
            self: Para encadeamento de métodos
        """
        if n >= 0:
            self.params['$skip'] = n
        return self
    
    def expand(self, *entities: str) -> 'ODataQueryBuilder':
        """
        Expande entidades relacionadas ($expand)
        
        Args:
            *entities: Nomes das entidades a expandir
            
        Returns:
            self: Para encadeamento de métodos
        """
        if entities:
            self.params['$expand'] = ','.join(entities)
        return self
    
    def count(self, enabled: bool = True) -> 'ODataQueryBuilder':
        """
        Solicita contagem total de registros ($count)
        
        Args:
            enabled: True para incluir contagem
            
        Returns:
            self: Para encadeamento de métodos
        """
        self.params['$count'] = str(enabled).lower()
        return self
    
    def get(self) -> Dict[str, Any]:
        """
        Executa a consulta GET
        
        Returns:
            Dicionário com os resultados da consulta (resposta total do servidor)
        """
        return self.client._request('GET', self.entity_name, params=self.params)
    
    def first(self) -> Optional[Dict[str, Any]]:
        """
        Retorna apenas o primeiro resultado ($top=1)
        
        Returns:
            Dicionário com o primeiro resultado ou None se vazio
        """
        self.top(1)
        result = self.get()
        values = result.get('value', [])
        return values[0] if values else None
    
    def count_only(self) -> int:
        """
        Retorna apenas o número total de registros ($count=true e $top=0)
        
        Returns:
            Número total de registros que atendem ao filtro
        """
        self.count(True)
        self.top(0)
        result = self.get()
        return result.get('@odata.count', 0)