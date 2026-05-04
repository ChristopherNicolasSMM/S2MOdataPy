"""
Exceções customizadas para S2MOdataPy

Author: Christopher N. S. M. Mauricio
"""


class S2MODataError(Exception):
    """
    Exceção base para todos os erros do S2MOdataPy.

    Attributes:
        message (str): Descrição legível do erro.
        details (dict): Informações adicionais (status_code, url, etc.).
    """

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            return f"{self.message} | Detalhes: {self.details}"
        return self.message


class S2MODataConnectionError(S2MODataError):
    """
    Erro de conexão com o servidor OData.

    Levantada quando o servidor está inacessível ou a URL está incorreta.
    """
    pass


class S2MODataNotFoundError(S2MODataError):
    """
    Recurso não encontrado no servidor (HTTP 404).

    Levantada quando a entidade ou o registro solicitado não existe.
    """
    pass


class S2MODataValidationError(S2MODataError):
    """
    Erro de validação nos dados enviados ao servidor.

    Levantada quando o servidor rejeita os dados por violação de regras
    de negócio ou de schema (HTTP 400/422).
    """
    pass


class S2MODataAuthenticationError(S2MODataError):
    """
    Erro de autenticação ou autorização (HTTP 401/403).

    Levantada quando as credenciais são inválidas ou insuficientes
    para acessar o recurso solicitado.
    """
    pass


class S2MODataParseError(S2MODataError):
    """
    Erro ao processar a resposta do servidor.

    Levantada quando o conteúdo retornado não pode ser interpretado
    como JSON ou XML válido.
    """
    pass
