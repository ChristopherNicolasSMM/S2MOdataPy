"""
Exceções customizadas para S2MOdataPy
Author: Christopher N. S. M. Mauricio
"""


class S2MODataError(Exception):
    """Exceção base para erros do S2MOdataPy"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class S2MODataConnectionError(S2MODataError):
    """Erro de conexão com o servidor OData"""
    pass


class S2MODataNotFoundError(S2MODataError):
    """Recurso não encontrado (404)"""
    pass


class S2MODataValidationError(S2MODataError):
    """Erro de validação nos parâmetros da consulta"""
    pass


class S2MODataAuthenticationError(S2MODataError):
    """Erro de autenticação (401/403)"""
    pass